## How to Verify

All temp files go in `_tmp/gemma4_26b/` under the current directory. Create it if it doesn't exist.

I want to test if you can do multi-step agentic tasks, because this is using ollama with gemma4:26b model in claude code. Please do each test one by one, tick or cross the boxes when done.

| Test area             | Test prompt                                                                                                                                                                                                                                                                                                                                                                                  | Works? |
|-----------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------|
| Multi-step chaining   | There is a DuckDB file at /mnt/e/code/_notes/ai-agents/.claude/skills/tool__local_claude_code/assets/verification/sample.duckdb. Inspect its schema. All tables share a common join key but the column is named differently in each table — figure out which columns match by inspecting the data. Run a JOIN query that combines data from at least 2 tables, present 5 rows of results, then export those rows as JSON to _tmp/gemma4_26b/verify_result.json. |        |
| Large output handling | Read all files in this directory recursively, count total lines of code per file type, and present a summary table sorted by line count descending.                                                                                                                                                                                                                                          |        |
| Instruction following | Read _tmp/gemma4_26b/verify_result.json. Reformat it as a markdown table. Sort alphabetically by the first column. Output to _tmp/gemma4_26b/verify_result.md. The file must have exactly these 3 lines at the top: a h1 title, a blank line, then the table. No other content.                                                                                                                                    |        |
| Error recovery        | Read _tmp/gemma4_26b/this_file_does_not_exist.txt. If it fails, create it with the content "recovered", then read it again to confirm.                                                                                                                                                                                                                                                                  |        |
| Code correctness      | Write a Python script at _tmp/gemma4_26b/verify_stats.py that reads /mnt/e/code/_notes/ai-agents/.claude/skills/tool__local_claude_code/assets/verification/sample.duckdb, calculates the average headcount per organisation status, and prints the result formatted to 1 decimal place. Run it.                                                                                                                                                                                              |        |
| Complex editing       | Create two files: _tmp/gemma4_26b/verify_config.json with {"host": "localhost", "port": 3000, "debug": true} and _tmp/gemma4_26b/verify_app.py that reads that config and prints each key-value pair. Then change the port to 8080 in the JSON file and change verify_app.py to also print "Config loaded successfully" at the end. Run verify_app.py to confirm both changes work.                                |        |

---

## Results: gemma4:26b — YYYY-MM-DD

| Test area             | Works? | Notes |
|-----------------------|--------|-------|
| Multi-step chaining   |        |       |
| Large output handling |        |       |
| Instruction following |        |       |
| Error recovery        |        |       |
| Code correctness      |        |       |
| Complex editing       |        |       |
