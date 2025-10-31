# Python Performance Rules for Large-Scale Data Processing

This document extracts key performance optimization patterns for ETL (Extract, Transform, Load).

1. (E) Reading
2. (E) Filtering
3. (E) Sorting
4. (ETL) Pattern for DuckDB-to-DuckDB ETL - When python code transformation is not needed
5. (T) Structure Creation
6. (T) Repeated Computations
7. (T) Batch Transformer Class
8. (L) Bulk Inserts - new table
9. (L) Bulk Inserts - existing table - (create/append + join/append)
10. (L) Bulk Update (When unavoidable)
11. Resumability Architectural Pattern
12. Bottleneck Identification with SimplerTimer

---

## 1. Data Reading Strategy (I/O vs. Memory)

When a large dataset is needed multiple times throughout a process:

- **Analyze the Trade-off:**
    - **Scenario A (Dataset fits in RAM):** If the entire dataset can be loaded into memory without issue, load it **once** at the start of the process.
        - **Reason:** This minimizes slow disk I/O. Reading from RAM is orders of magnitude faster than reading from disk, so avoiding repeated disk reads is a huge performance win.
    - **Scenario B (Dataset >> RAM):** If the dataset is too large for memory, you must process it in chunks, accepting the higher I/O cost.
        - **Reason:** Attempting to load too much data will cause the program to fail or thrash system memory (swapping), which is extremely slow.

- **Decision Rule:**
    - **ALWAYS load once** if the dataset fits in available RAM and is needed multiple times
    - **ALWAYS use chunked/batched processing** if the dataset exceeds available RAM
    - To decide: Check dataset size vs. available memory. If dataset is <50% of available RAM, it's safe to load once.

---

## 2. Data Filtering

When selecting a subset of data from a large table for processing:

- **Avoid:** Loading the entire table into memory and then filtering it in Python.
    - **Reason:** Inefficient use of memory and data transfer. The filtering operation itself is also slower in Python than in the database engine.

- **Use:** Push the filtering logic down to the database layer using a `WHERE` clause in the SQL query.
    - **Reason:** The database can use indexes and optimized filtering logic to return only the data you need, minimizing I/O and memory usage.

- **Example:**
  ```python
  # GOOD: Filtering is done in SQL
  def get_assignments(self, resume_from: str) -> pd.Series:
      query = "SELECT * FROM my_table"
      if resume_from:
          query += f" WHERE CompanyNumber > '{resume_from}'" # Filter in DB
      # ... execute query ...

  # BAD: Filtering is done in Python
  def get_assignments(self) -> pd.Series:
      query = "SELECT * FROM my_table" # Loads everything
      df = conn.execute(query).fetch_df()
      if last_processed:
          df = df[df.index > last_processed] # Filter in memory
  ```

---

## 3. Data Sorting and Order Integrity

In any batch processing workflow, maintaining a stable and consistent sort order is critical for both performance and data integrity.

- **Avoid:** Sorting data in Python after it has been fetched from the database (e.g., using `sorted()` or `.sort()`).
    - **Reason (Data Integrity):** This is the primary concern. Python and SQL may have different sorting behaviors (e.g., for case sensitivity, special characters, or tie-breaking). Relying on Python to sort data that was not ordered by the database can lead to an inconsistent order between batches. This can break keyset pagination and cause records to be skipped or processed multiple times.
    - **Reason (Performance):** Pushing the sorting to the database allows it to use indexes, which is significantly faster than performing a large sort in Python's memory.

- **Use:** A mandatory `ORDER BY` clause in the SQL query that fetches the data.
    - **Reason:** This establishes the database as the single source of truth for data ordering, guaranteeing that every batch is processed in a consistent, predictable, and reliable sequence.

- **Example:**
  ```python
  # GOOD: Order is guaranteed by the database
  def get_records(self, last_seen_id: int) -> list:
      # The ORDER BY clause is mandatory for reliable pagination
      query = "SELECT * FROM my_table WHERE id > ? ORDER BY id ASC LIMIT 100"
      return conn.execute(query, [last_seen_id]).fetchall()

  # BAD: Order is not guaranteed, prone to data integrity errors
  def get_records(self) -> list:
      query = "SELECT * FROM my_table" # No ORDER BY!
      records = conn.execute(query).fetchall()
      # Sorting in Python later is unreliable and slow
      return sorted(records, key=lambda x: x.id)
  ```

---

## 4. Pattern for DuckDB-to-DuckDB ETL - When python code transformation is not needed

When the source and destination for an ETL process are both DuckDB databases, a specialized, high-performance pattern should be used. This approach avoids common pitfalls related to data type handling that occur when data is moved out of the database into a client application (like Python/pandas) and then back in.

- **Avoid:** The "data round-trip" pattern: `SELECT` from source DB -> Load into pandas DataFrame -> `register()` DataFrame -> `INSERT` into target DB.
    - **Reason:** This pattern is the root cause of subtle and severe bugs. DuckDB's type inference on the temporary table created by `register()` is unpredictable for complex nested types (e.g., `STRUCT`s). If a batch contains all `NULL` values for a nested field, DuckDB may infer a `NULL` data type for that field, causing `INSERT` failures on subsequent batches that contain actual data. This issue is extremely difficult to debug.

- **Required Pattern:** A pure, in-database transformation using `ATTACH`.
    - **Implementation:** The entire ETL operation is consolidated into a single SQL query that runs on the **target** database connection.
        1.  **`ATTACH` Source DB:** The source DuckDB file is `ATTACH`ed with an alias (e.g., `input_db`). This makes its tables accessible.
        2.  **`INSERT INTO ... SELECT`:** A single `INSERT` statement is executed. The `SELECT` clause reads from the attached database (e.g., `FROM input_db.my_table`).
    - **Reason (Correctness):** This completely bypasses the problematic Python/pandas layer, eliminating all type inference issues. The data never leaves the DuckDB engine.
    - **Reason (Performance):** This is dramatically faster as it avoids the massive overhead of serializing data out to Python, allocating memory for a DataFrame, and then having DuckDB re-ingest the data.

- **Handling Complex Transformations:** If the transformation is complex (e.g., casting unsupported types within a `STRUCT`), use DuckDB's built-in functions within the `SELECT` statement.
    - **Example:** To handle `STRUCT` fields that are not natively supported (like spatial types), use `list_transform` to rebuild the struct on the fly.

- **Example (Conceptual):**
  ```python
  # 1. Connect to the TARGET database
  con = duckdb.connect(database='target.duckdb', read_only=False)

  # 2. ATTACH the source database
  con.execute("ATTACH 'source.duckdb' AS input_db (READ_ONLY);")

  # 3. Execute a single, powerful query
  # This query reads from input_db, transforms, and inserts into the target table.
  insert_query = """
  INSERT INTO main.target_table (id, aggregated_data)
  SELECT
      id,
      -- Perform transformations on the fly
      list_transform(
          aggregated_list,
          s -> { 'field_a': CAST(s.field_a AS VARCHAR), ... }
      )
  FROM (
      -- Subquery performs the initial aggregation
      SELECT id, LIST(s) as aggregated_list
      FROM input_db.source_table s
      GROUP BY id
  );
  """
  con.execute(insert_query)
  con.close()
  ```

---

## 5. Data Structure Creation

When creating a list of structured records from columnar data (e.g., pandas Series, numpy arrays):

- **Avoid:** Row-by-row iteration using Python loops (e.g., `for`/`zip`).
    - **Reason:** Python loops have high interpreter overhead for each row, making them very slow for large datasets.

- **Use:** Direct construction of a pandas DataFrame from the source columns.
    - **Reason (Performance):** This uses fast, vectorized operations that run in C, avoiding Python-level loops entirely.
    - **Reason (Data Integrity):** This pattern inherently respects and preserves the sort order of the input columns. This is critical for ensuring that the output data structure correctly aligns with the order established by the SQL `ORDER BY` clause (Rule #3).

- **Example:**
  ```python
  # GOOD: Vectorized DataFrame creation
  predictions_df = pd.DataFrame({
      'col_a': numpy_array_of_scores,
      'col_b': pandas_series_of_ids
  })

  # BAD: Slow Python loop
  predictions = []
  for id, score in zip(pandas_series_of_ids, numpy_array_of_scores):
      predictions.append({'col_a': score, 'col_b': id})
  ```

---

## 6. Avoid Repeated In-Loop Computations (Simple Cases)

When processing data in a loop, any computation that is repeated with the same inputs should be moved outside the loop.

**When to use this pattern:**
- **ONLY for simple cases** where you need to pre-compute a single lookup structure (one dict or one set)
- The loop body is straightforward with minimal additional processing

**When NOT to use this pattern:**
- If you need **multiple** pre-computed structures (multiple dicts/sets) -> Use Rule #6 (Batch Transformer)
- If you need a **template object pattern** -> Use Rule #6 (Batch Transformer)
- If you have **nested loops** or **complex transformations** -> Use Rule #6 (Batch Transformer)

---

- **Avoid:** Re-computing the same value or calling the same function on the same data inside a loop.
    - **Reason:** This creates unnecessary computational overhead on every single iteration, which adds up significantly over large datasets.

- **Use:** Pre-computing the result once before the loop begins and storing it in a variable or a lookup structure (like a dictionary or set).
    - **Reason:** This "hoists" the invariant computation out of the loop, paying the cost only once instead of millions of times.

- **Example:**
  ```python
  # GOOD: Simple case with a single pre-computed lookup
  # Pre-compute status labels for all known user IDs
  user_status_map = {user.id: get_status_label(user) for user in all_users}

  # Process transactions using the pre-computed map
  for transaction in transactions:
      user_id = transaction.user_id
      status = user_status_map.get(user_id, "unknown")
      # ... process transaction with status ...

  # BAD: The get_status_label() function is called repeatedly for the same user IDs
  for transaction in transactions:
      user_id = transaction.user_id
      # Slow! If user_123 has 1000 transactions, this calls get_status_label() 1000 times
      status = get_status_label(get_user(user_id))
      # ... process transaction with status ...
  ```

---

## 7. Use a Batch Transformer Class for In-Loop Processing

**When to use this pattern:**
- **DEFAULT approach** for any row-by-row processing that involves loop-invariant operations
- **MANDATORY** when the code has nested loops or needs to loop multiple times over the same data
- **MANDATORY** when creating lookup structures (dicts, sets) or calling transformation functions inside the loop

**Only skip this pattern for:**
- Extremely simple, single-operation transformations (e.g., `[x * 2 for x in values]`)
- Transformations that are already fully vectorized (e.g., pure pandas/numpy operations)

---

### Pattern Overview

Create a dedicated "Batch Transformer" class that gets initialized **once** before the loop begins to pre-compute all invariant structures.

- **Key Techniques:**
    1. **Pre-computation in `__init__`:** The constructor pre-computes all loop-invariant data (lookup dicts, sets, sanitization maps, compiled regex, etc.)
    2. **Template Object Pattern:** Pre-build a template dict/object with default values, then use fast shallow `.copy()` for each row

- **Performance Warning on Template Copy Strategy:**
    - **ALWAYS use shallow `.copy()`** for the template pattern. This is fast (constant time for dict keys).
    - **NEVER use `copy.deepcopy()`** in batch processing loops - it defeats the performance optimization.
    - **If your template contains mutable nested objects (lists, dicts), this is a RED FLAG** - you likely have a design problem that will cause performance issues or bugs. Rethink the transformation approach to work with flat, immutable template values.

---

### Example

```python
# GOOD: A dedicated class pre-computes everything.
class MyBatchTransformer:
    def __init__(self, columns, column_prefix):
        """
        Pre-compute all invariant structures once.

        Args:
            columns: List of column names to process
            column_prefix: Prefix for output column names
        """
        # 1. Pre-compute a lookup map (column_name -> sanitized_name)
        self.sanitized_map = {c: sanitize(c) for c in columns}

        # 2. Pre-compute a set for fast O(1) membership checks
        self.columns_set = set(columns)

        # 3. Pre-build a template dictionary with all default values
        # IMPORTANT: Template values must be immutable (int, str, float, bool, None)
        # NOT mutable objects (list, dict, set) - see warning above
        self.template = {f"{column_prefix}{self.sanitized_map[c]}": 0 for c in columns}

        self.column_prefix = column_prefix

    def transform_row(self, row_values):
        """
        Transform a single row using pre-computed structures.

        Args:
            row_values: List of values present in this row

        Returns:
            Dict with all columns (template keys) where matching values set to 1
        """
        # Fast shallow copy of template (O(1) for dict structure)
        result = self.template.copy()

        # Only process values that exist in our columns set
        for value in row_values:
            if value in self.columns_set:
                # Use pre-computed sanitized name
                sanitized_key = self.sanitized_map[value]
                result[f"{self.column_prefix}{sanitized_key}"] = 1

        return result

# Usage:
transformer = MyBatchTransformer(all_columns, "PREFIX_")  # Initialized ONCE
all_results = []
for row in all_rows:
    # Fast transformation using pre-computed assets
    transformed_row = transformer.transform_row(row.values)
    all_results.append(transformed_row)


# BAD: All the setup work is repeated for every row.
all_results = []
for row in all_rows:
    # ANTI-PATTERN: Creating the same structures in every iteration
    sanitized_map = {c: sanitize(c) for c in all_columns}  # X - Repeated computation
    columns_set = set(all_columns)  # X - Repeated set creation
    result = {f"PREFIX_{sanitized_map[c]}": 0 for c in all_columns}  # X - Repeated dict construction

    for value in row.values:
        if value in columns_set:
            result[f"PREFIX_{sanitized_map[value]}"] = 1
    all_results.append(result)
```

---

## 8. Bulk Database Inserts (DuckDB)

For bulk `INSERT` operations into DuckDB:

- **Avoid:** The standard DB-API `cursor.executemany()` method.
    - **Reason:** Significantly slower (~189x) than optimized methods.

- **Prefer:** `connection.append()` method with a pandas DataFrame.
    - **Reason:** Leverages DuckDB's C++ backend for high-speed, vectorized data ingestion.
    - **Limitation:** Cannot be used with tables that have auto-generated DEFAULT columns (e.g., `_auto_id` with SEQUENCE).

- **Alternative:** `register() + INSERT SELECT` pattern when you need to exclude columns with DEFAULT values.
    - **Use when:** Table has `_auto_id` with SEQUENCE and you need `COUNT(*) == MAX(_auto_id)` verification.
    - **Implementation:** Register DataFrame as temp view, INSERT only non-auto columns, unregister.

- **Examples:**
  ```python
  # GOOD: Fast append (no auto-generated columns)
  def append_predictions(self, predictions_df: pd.DataFrame) -> None:
      with self.get_connection() as conn:
          conn.append('my_table', predictions_df)

  # GOOD: Register pattern (table has _auto_id for verification)
  def insert_batch(self, table_name: str, batch: SourceDataBatch) -> int:
      df = pd.DataFrame(batch.rows)
      if '_auto_id' in df.columns:
          df = df.drop(columns=['_auto_id'])

      with self.get_connection() as conn:
          conn.register('temp_batch', df)
          column_names = ', '.join(df.columns)
          conn.execute(f"INSERT INTO {table_name} ({column_names}) SELECT * FROM temp_batch")
          conn.unregister('temp_batch')
      return batch.row_count

  # BAD: Slow, non-optimal for DuckDB
  def store_predictions_batch(self, predictions: list[dict]) -> None:
      conn.executemany(insert_sql, batch_data)
  ```

---

## 9. Architectural Pattern: Use Append-Only Workflows

This is the primary architectural principle for data enrichment and transformation pipelines.

- **Principle:** When adding new data or features (e.g., new columns) to an existing dataset, the `ALTER TABLE ... ADD COLUMN` followed by `UPDATE` pattern **MUST be avoided**.

- **Required Pattern:** Treat data as immutable by creating new, separate tables for new features, and then joining them as needed.
    1. **Step 1: Isolate new features in a new table.** The process should generate the new data and save it to a *new, separate table*, typically containing `(primary_key, new_feature_1, new_feature_2, ...)`. This is a fast, append-only `CREATE TABLE AS SELECT ...` or `INSERT` operation.
    2. **Step 2 (Optional): Consolidate data by joining.** If a final, wide table is required by a downstream process, it should be created as a *third* artifact by `JOIN`ing the original base table with the new feature table(s). This consolidation is also an append-only `CREATE TABLE AS SELECT ...` operation.

- **Reasoning:** This approach is preferred for its superior performance, maintainability (it's easier to debug/re-run a step that creates one small table), flexibility (easier to add more features later), and resilience (it is non-destructive).

- **Example:**
  ```sql
  -- INSTEAD OF THIS (BAD):
  ALTER TABLE EnrichedCompanies ADD COLUMN phone_features TEXT;
  UPDATE EnrichedCompanies SET phone_features = ...;

  -- DO THIS (GOOD):
  -- Step 1: Create a new, separate table for the new features.
  CREATE TABLE CompanyPhoneFeatures AS
  SELECT company_pk, <phone_features>
  FROM source_phone_data;

  -- Step 2 (if needed): Create the final table by joining.
  CREATE TABLE FinalEnrichedCompanies AS
  SELECT T1.*, T2.phone_features
  FROM EnrichedCompanies T1
  JOIN CompanyPhoneFeatures T2 ON T1.pk = T2.company_pk;
  ```

---

## 10. Implementation: High-Performance Bulk Updates

This rule applies **only** in legacy situations or specific cases where the append-only architecture (Rule #8) is not feasible.

- **Avoid:** Performing `UPDATE` statements one by one in a loop. This is the slowest possible method.

- **Use:** The high-performance "UPDATE FROM" pattern with a temporary view.
    - **Implementation:** Create a pandas DataFrame in Python containing the `(primary_key, new_value)` pairs for all rows to be updated. `register()` this DataFrame as a temporary view in DuckDB, then execute a single `UPDATE ... FROM` statement that joins the target table with the temporary view.

- **Example:**
  ```python
  # This pattern should only be used when updates are absolutely necessary.
  def bulk_update_records(self, updates_df: pd.DataFrame) -> None:
      with self.get_connection() as conn:
          conn.register('temp_updates_view', updates_df)
          update_sql = """
          UPDATE main_table
          SET value_column = temp_updates_view.new_value
          FROM temp_updates_view
          WHERE main_table.pk = temp_updates_view.pk;
          """
          conn.execute(update_sql)
          conn.unregister('temp_updates_view')
  ```

---

## 11. Architectural Pattern: Design for Resumability

Any batch process expected to run for a significant amount of time (e.g., >15-30 minutes) **MUST** be designed to be resumable to protect against interruptions (e.g., crashes, manual stops, deployments).

- **Reason:** A resumable design saves hours of lost work, improves operational flexibility, and makes the entire system more robust and reliable.

- **Required Implementation:** A robust resumability strategy requires two levels of tracking:

    1. **Task-Level Resumability (Coarse-Grained):** For processes that iterate through a list of high-level tasks (e.g., processing 50 RTICs).
        - **Mechanism:** Use a dedicated "progress tracking" table (e.g., `completed_tasks`) that stores the ID of each task that has been *fully* completed.
        - **Logic:** At the start of the run, query this table to get a list of completed task IDs. Exclude these IDs from the main list of tasks to be processed.

    2. **Intra-Task Resumability (Fine-Grained):** For processing a large number of records *within* a single task (e.g., processing 200,000 companies for one RTIC).
        - **Mechanism:** This pattern relies on other rules: committing results in batches (Rule #7) and consistent sorting (Rule #3).
        - **Logic:** Before starting the work inside a task, query the destination table to find the last successfully processed primary key (`MAX(pk)`). Use this key in the data-reading query (`WHERE pk > ?`) to ensure you only fetch records that have not yet been processed.

---

### Implementation Details: Efficient Keyset Pagination

The intra-task resumability pattern requires careful SQL construction for both correctness and performance:

1. **Combine Work-Finding + Keyset Pagination:**
   - The query **MUST** combine two `WHERE` conditions:
     - **Work-finding predicate:** `WHERE processed_column IS NULL` (identifies unprocessed records)
     - **Keyset pagination predicate:** `WHERE pk > ?` (uses last-seen primary key for efficient iteration)
   - Both predicates working together enable efficient, resumable batch processing

2. **Index Optimization Strategy (The "Clever Trick"):**
   - **Indexing a value** (`pk > 'value'`): Allows the database to jump directly to a specific row position using the index (fast O(log n) lookup)
   - **Indexing a condition** (`processed_column IS NULL`): Requires scanning because the position of NULL values is dynamic (potentially slow O(n) scan)
   - **Combining both** (`WHERE pk > ? AND processed_column IS NULL`): The database uses the index to jump to the keyset position, then scans for NULL values from that point forward. Since processing is sequential, the first record at the keyset position is typically the next unprocessed record, making the NULL scan minimal.

3. **Respect Database Ordering (Critical):**
   - Code **MUST** preserve the exact order returned by the SQL `ORDER BY` clause
   - **NEVER re-sort records in Python** after fetching from the database - Python and SQL may use different sorting semantics (see Rule #3)
   - When tracking the last-seen key, use the last element from the batch as-is: `last_pk = batch_records[-1].pk`
   - This assumes the list order matches the SQL order, which is only guaranteed if you don't re-sort in code

4. **Standard Query Pattern:**
   ```sql
   SELECT pk, data_column, processed_column
   FROM my_table
   WHERE pk > ? AND processed_column IS NULL
   ORDER BY pk ASC
   LIMIT ?
   ```

5. **Resume Behavior:**
   - **Mid-task restart:** If the process crashes and restarts during a task, `last_pk` is lost (in-memory). The query falls back to `WHERE pk > 0 AND processed_column IS NULL`, which works correctly but scans from the beginning to find the first unprocessed record (slower on restart, but correct).
   - **Across-task restart:** Completed tasks are tracked persistently in the `completed_tasks` table, so they are skipped entirely (fast).

---

- **Example (Conceptual):**
  ```python
  # 1. Task-Level Resumability
  all_rtic_codes = get_all_rtics_from_source()
  completed_rtic_codes = repository.get_completed_rtics() # Reads from tracking table
  remaining_rtics = [r for r in all_rtic_codes if r not in completed_rtic_codes]

  for rtic in remaining_rtics:
      # 2. Intra-Task Resumability
      last_processed_company = repository.get_last_processed_company(rtic) # MAX(pk) from output table

      # Fetch only the data that needs processing
      companies_to_process = repository.get_companies_for_rtic(
          rtic_code=rtic,
          resume_from=last_processed_company # Adds 'WHERE pk > ?' to query
      )

      for batch in companies_to_process:
          # ... process batch ...
          repository.save_batch(batch) # Commits progress incrementally

      # Mark the high-level task as complete in the tracking table
      repository.mark_rtic_completed(rtic)
  ```

---

## 12. Instrumentation: Use `SimplerTimer` for Bottleneck Analysis

- To identify bottlenecks, batch processing logic MUST be wrapped in a `SimplerTimer`
- Key operations within the block MUST be demarcated with timer.track()
