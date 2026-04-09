# Action: Web Fetch

Fetch a URL and return cleaned text content (HTML/CSS/JS stripped, boilerplate removed, deduplicated).

## Usage

```bash
${CLAUDE_SKILL_DIR}/scripts/web_fetch.sh "https://example.com"
```

Returns clean text extracted from the page. The text cleaner removes:
- HTML tags, CSS, JavaScript
- Duplicate paragraphs and sentences
- Repeated navigation/footer phrases
- Metadata patterns

## Quality filter

Pages with very little content (< 100 chars or < 20 words after cleaning) will show a notice that the quality filter rejected the text, followed by the cleaned text anyway.
