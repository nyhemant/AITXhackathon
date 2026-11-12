# Download metric

Weekly downloads are the sum of two GA4 events:

- `printable_download`
- `mission_printed`

Do not add `file_download` or `page_print` to that sum. Those events count the same print and the same download a second time.

## Per page in GA4

Both events send `page_path`: the path only, with no query and no fragment (for example `/field-pack/lincoln-park-zoo/`). GA4 also attaches `page_location` on its own. That built-in Page path can include a query string. In Explore, break the event out by the event parameter `page_path` when the place path should stay one row.

`mission_printed` also sends `venue` (the place slug, same value as `venue_slug`).

In Explore: start from the event name, add the dimension for the event parameter `page_path`, and split `printable_download` from `mission_printed`. One place is one path, such as `/field-pack/amnh/`.

## Server counter

Server PDF GETs are a second line, kept apart from the GA4 total. A GET of a file under `/printables/pdf/` that passes the counter rules is stored in `pdf-counts-YYYY-MM.json` (date in America/Chicago). Each PDF key is `letter/<stem>` or `a4/<stem>` with counts `site`, `search`, and `other` from the Referer host only.

When that host is kidzookit.com or a subdomain, the same row also stores `pages`: the referring path only. The query and fragment are removed. The path is percent-decoded, lowercased, dot-segments are removed, repeated slashes collapse, a trailing slash stays, and the result is cut at 120 characters. A path that does not match `^/[a-z0-9/_-]*$` is stored as `other-page`. Search hosts and every other host do not get a `pages` entry.

```json
{"2026-11-12": {"letter/scavenger-hunt": {"site": 2, "search": 1, "other": 0, "pages": {"/field-pack/lincoln-park-zoo/": 2}}}}
```

`site`, `search`, and `other` stay integer counts. `pages` is an extra key on the same object.

The file stores counts only — no IP, user agent, full referrer, or query string.

Read it on the server (SSH):

```bash
python3 scripts/pdf_counts_report.py
python3 scripts/pdf_counts_report.py --dir ~/.kidzookit/counts
```

The report prints weekly totals (Monday–Sunday, America/Chicago dates already on the keys, summed `site` + `search` + `other`) and per-page totals from every `pages` map in the counts directory. The directory is `$KZK_COUNTS_DIR` when that is set, otherwise `~/.kidzookit/counts`.
