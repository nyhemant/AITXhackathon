# Venue data & presence confidence

## Live print lists (`venues/*.json`)

Authoritative for mission sheets and SEO start-here cards.

| Field | Meaning |
|-------|---------|
| `list_confidence` | `audited` · `partial` · `template` |
| `items[].presence` | `verified` · `high` · `medium` · `template` · `absent` |
| `do_not_list` | Never print these names/catalog ids |
| `last_presence_audit` | Date of collection check |

**Engine rule:** named finds need `presence` ≥ high/verified (or venue `audited` / owner `partial` grandfather). Template zoo packs render **wonder** finds until audited.

Report: `python3 scripts/audit_presence_report.py`

## Shortlist candidates (planning only)

**Partially wired** via manual audits → `venues/*.json`. Used for content planning and accuracy work.

## Files
| File | Use |
|------|-----|
| `venue-shortlist-candidates.json` | Full structured DB |
| `venue-shortlist-candidates.csv` | Spreadsheet-friendly flat export |

## Priority (visitor planning)
1. Must-see / first ~60–90 min with young kids  
2. High value if energy allows  
3. Mid-visit  
4. If time  
5. Optional — or **do not promise** if notes say absent  

## Confidence
- `verified` — checked this research pass  
- `high` — strong secondary / long-standing  
- `medium` — likely; confirm before publish  
- `template` — type-based starter, not venue-audited  

## `research_priority` (which venues to deepen next)
Lower number = higher content ROI (1 = flagship accuracy risk / tourist demand).

## Regenerating
Built from `places-data.js` + `catalog.js` plus hand research blocks in the generator script session. Re-run research when official collections change (e.g. pandas).
