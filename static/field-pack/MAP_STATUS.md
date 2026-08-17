# National park map status
Updated: 2026-08-17

## Summary
- **US parks:** 63/63 local map images; **14/63** deep-link to a PDF
- **International:** 15/15 have maps
  - Real/cartographic sources: **11**
  - OSM orientation fallbacks: **4**

## Display model
- Site/print show **cropped map image** under `/field-pack/media/maps/{slug}.jpg`
- Link uses `visitor_map_page` → full PDF when available, else official maps page
- Smart crop: `scripts/crop_park_map.py` (map page pick + chrome trim)
- Fetch: `scripts/fetch_nps_park_maps.py`

## International parks

| slug | tier | size | deep link |
|------|------|------|----------|
| banff | cartography | 961x1140 | https://parks.canada.ca/pn-np/ab/banff |
| blue-mountains | OSM | 1280x1280 | https://www.nationalparks.nsw.gov.au/visit-a-park/ |
| fiordland | cartography | 1623x2200 | https://www.doc.govt.nz/parks-and-recreation/place |
| fuji-hakone-izu | OSM | 1280x1280 | https://www.env.go.jp/en/nature/nps/park/fujihakon |
| iguazu-argentina | cartography | 2200x1462 | https://www.argentina.gob.ar/interior/ambiente/par |
| jasper | cartography | 2115x2200 | https://parks.canada.ca/pn-np/ab/jasper |
| killarney | OSM | 1280x1280 | https://www.nationalparks.ie/killarney/ |
| kruger | cartography | 934x2071 | https://www.sanparks.org/parks/kruger |
| lake-district | cartography | 1826x2200 | https://www.lakedistrict.gov.uk/ |
| nikko | OSM | 1280x1280 | https://www.env.go.jp/en/nature/nps/park/nikko/ |
| plitvice-lakes | cartography | 1012x1373 | https://np-plitvicka-jezera.hr/en/ |
| snowdonia | cartography | 1687x2200 | https://www.eryri.llyw.cymru/ |
| table-mountain | cartography | 950x1302 | https://www.sanparks.org/parks/table-mountain/trav |
| torres-del-paine | cartography | 2200x1688 | https://torresdelpaine.com/wp-content/uploads/site |
| yoho | cartography | 2115x2200 | https://parks.canada.ca/pn-np/bc/yoho |

## US PDF deep links

- `american-samoa`: https://www.nps.gov/npsa/planyourvisit/upload/Area_Map.pdf
- `black-canyon-gunnison`: https://www.nps.gov/blca/planyourvisit/upload/Black_Canyon_unigrid_2023_508_web.pdf
- `capitol-reef`: https://www.nps.gov/care/planyourvisit/upload/CARE_Unigrid-map-2021.pdf
- `gates-of-arctic`: https://www.nps.gov/carto/hfc/carto/media/gaarmap1.pdf
- `grand-canyon`: https://www.nps.gov/grca/planyourvisit/upload/GRCAmap2.pdf
- `great-smoky-mountains`: https://www.nps.gov/grsm/planyourvisit/upload/grsmmap_2024_reduced_508.pdf
- `kings-canyon`: https://www.nps.gov/seki/planyourvisit/upload/20210826-Unigrid-Spanish-508.pdf
- `north-cascades`: https://www.nps.gov/noca/planyourvisit/upload/Ross_Lake_Trip_Planner_for_Website_508.pdf
- `pinnacles`: https://www.nps.gov/pinn/planyourvisit/upload/2019-map-update-DRAFT-2.pdf
- `sequoia`: https://www.nps.gov/seki/planyourvisit/upload/20210826-Unigrid-Spanish-508.pdf
- `white-sands`: https://www.nps.gov/whsa/planyourvisit/upload/WHSA_Unigrid_2022.pdf
- `wrangell-st-elias`: https://www.nps.gov/wrst/learn/photosmultimedia/upload/WRST_Unigrid_English-508.pdf
- `yellowstone`: https://www.nps.gov/yell/planyourvisit/upload/2025_Yellowstone-Unigrid_Web-508.pdf
- `zion`: https://www.nps.gov/zion/planyourvisit/upload/ZionUnigrid.pdf

## Remaining gaps (accepted)
- Some US parks have no clean park-wide PDF on maps.htm — link stays on maps.htm
- 4 intl parks use denser OSM orientation maps (Blue Mountains, Fuji, Killarney, Nikkō). Rechecked 2026-08-17: NSW / Japan MoE / NPWS visitor maps are not freely licensable for hosting, so OSM stays.
- Fiordland uses NZ parks locator (no free high-res park unigrid found)
- Zoo/museum maps are separate product (brochure floor plans)
