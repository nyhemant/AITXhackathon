# Download metric

Weekly downloads are the sum of two GA4 events:

- `printable_download`
- `mission_printed`

Do not add `file_download` or `page_print` to that sum. Those events count the same print and the same download a second time.

Server PDF GETs are a second line, kept apart from the GA4 total. A GET of a file under `/printables/pdf/` that passes the counter rules is stored in `pdf-counts-YYYY-MM.json` (date in America/Chicago; bucket `site`, `search`, or `other` from the Referer host only). The file stores counts only — no IP, user agent, full referrer, or query string.
