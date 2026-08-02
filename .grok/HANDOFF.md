# 1Less — session handoff

**Last updated:** 2026-08-02 (Phase 3: logo + activation/retention)  
**Session:** `1less`  
**Pre-rearch restore:** `git checkout snapshot/pre-rearch-2026-08-02`

## Product
- **1Less** brand · **Baby's Day Out** default (`/` → `/field-pack/`) · **Dinner** secondary (`/dinner` via More)

## Shell
- `static/shell/` — logo **52px** (44px mobile), product name, More menu
- CSS cache: `shell.css?v=2`

## BDO landing
- Hook hero + Ready now cards + city chips + map
- Map ready venue: **Start outing** primary, Place info secondary
- Soon city: **Save this city** → `localStorage` `1less-saved-cities`
- Waiting line + continue last outing (deep-link `#/trip/id`)

## Planner
- Print treasure hunt promoted on home
- Win banner after submit/teach
- Storage: `1less-babys-day-out-trips-v1`

## Smoke
```bash
curl -sI http://localhost:8000/ | grep Location
curl -sf -o /dev/null -w "%{http_code}\n" http://localhost:8000/field-pack/ http://localhost:8000/dinner http://localhost:8000/shell/shell.css
```

## Next optional
- Email notify for saved cities
- `/outings` alias
- More ready packs

## Voice & polish
- Voice: no Arya; kid-neutral; print blank explorer name
- Ready cards static HTML fallback; logo 52px attrs
- Missions framed optional after visit; planner topbar compact under shell

