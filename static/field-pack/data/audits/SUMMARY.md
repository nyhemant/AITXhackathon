# Presence audit SUMMARY (batches 00–01)

Audited: 2026-08-08. Audit files only under `static/field-pack/data/audits/results/{slug}.json` — venue JSON/HTML not modified.

| slug | severity | confidence | content_mode | notes |
|------|----------|------------|--------------|-------|
| adelaide-zoo | critical | audited | curated | Official Adelaide Zoo list verifies pandas, tiger, giraffe, orangutan, otter; template African megafauna (lion, elephant, gorilla, chimp, ze |
| air-and-space | major | audited | curated | Core air/space stops (rockets, astronauts, How Things Fly, planetarium) verified. Drop Imaginarium leakage; treat shuttle orbiter as Udvar-H |
| al-ain-zoo | major | partial | hybrid | Lions, giraffes, elephants, hippos are high-confidence icons; several template species (gorilla, red panda, African penguin, Galápagos torto |
| albuquerque-biopark | critical | audited | curated | Strong official CABQ list: fix African→Asian elephant, Sumatran→Malayan tiger, drop African penguin and Galápagos tortoise; gorilla/giraffe/ |
| amnh | major | audited | curated | Dinosaur, mammal halls, planetarium verified. Drop live sloth; relabel rainforest dome and aquarium zone to real permanent halls (Biodiversi |
| antwerp-zoo | major | partial | hybrid | Elephants are Asian (not African); hippos are pygmy not Nile. Gorillas/chimps/giraffes strong. Several template species unclear — soft-label |
| aquarium-of-the-pacific | major | audited | curated | Shark Lagoon, jellies, turtles, penguins verified. Replace Asian small-clawed otter with sea otter; soft-label penguin species. |
| arizona-science-center | major | partial | hybrid | Hands-on/planetarium OK as science-center defaults; drop Imaginarium leakage and do not list space shuttle orbiter without confirmation. |
| artis-zoo | major | partial | hybrid | Gorillas verified; elephants are Asian; hippo house repurposed (no Nile hippo print target); tortoises Aldabra. Soft-label remaining templat |
| athens-attica-zoo | major | template | hybrid | Attica is a large collection zoo but official English species inventory was not fully enumerable this pass — keep hybrid/template confidence |
| auckland-zoo | critical | audited | curated | Official mammals list: tiger, lion, giraffe, zebra, red panda, otter verified. Elephants gone (Nov 2024). No gorilla/chimp/hippo on list — r |
| audubon-aquarium | minor | partial | hybrid | Standard aquarium targets are reasonable; otter remains unclear. Prefer curated marine icons over terrestrial template add-ons. |
| audubon-zoo | minor | partial | hybrid | Typical large AZA zoo icons likely present; full official species page not fully scraped — partial confidence, soft subspecies labels. |
| austin-zoo | critical | partial | curated | Rescue zoo with lions/tigers/tortoises/lemurs — NOT a template African safari set. Drop giraffe, hippo, cheetah, red panda, Sumatran-specifi |
| bangalore-bannerghatta | critical | partial | hybrid | Relabel to Asian elephant/Bengal tiger/lion; drop gorilla, chimp, African penguin. Template African suite is wrong for Bannerghatta. |
| bangkok-safari-world | minor | partial | hybrid | Safari World is a large drive-through + marine park; core safari herbivores/predators high-confidence; apes/penguins unclear. |
| barcelona-zoo | minor | audited | curated | Official animals list confirms African elephant, gorilla, lion, hippo, red panda; use Rothschild's giraffe label; soft-label tiger subspecie |
| beijing-zoo | minor | partial | hybrid | Pandas are verified icons; remaining list is plausible large-zoo template with partial confidence due to limited English official inventory. |
| berlin-zoo | minor | partial | hybrid | Feedings schedule verifies gorillas, chimps, hippos, elephants, pandas (pandas not even on current item list). Soft-label elephant/tiger spe |
| bogota-zoo | major | template | wonder | Jaime Duque is a theme park with zoo area north of Bogotá; official species inventory not verified — recommend wonder/template mode, not spe |
| bronx-zoo | minor | partial | curated | Flagship WCS zoo: gorilla/tiger/lion/giraffe/lemur/zebra/red panda high confidence; prefer Aldabra over Galápagos tortoise label. |
| budapest-zoo | minor | partial | hybrid | Large historic zoo; core megafauna high confidence from general knowledge/official presence but English species page not fully scraped — par |
| cairo-zoo | critical | template | wonder | No trustworthy official animal inventory; official_url is a Facebook root placeholder. Force wonder/template mode until a real source is att |
| cal-academy | ok | audited | curated | Osher Rainforest, Steinhart Aquarium, Morrison Planetarium verified on official exhibits page. Strong curated list. |
| calgary-zoo | critical | audited | curated | CRITICAL: no giant pandas, no elephants. Amur not Sumatran tigers. Verified: gorilla, lion, giraffe, hippo, zebra, red panda on official mam |
| california-science-center | ok | audited | curated | Endeavour + rockets verified flagships. Secondary habitat labels are softer — keep mission centered on space gallery. |
| carnegie-natural-history | major | partial | curated | Dinosaur halls are the correct centerpiece. Drop Imaginarium leakage; avoid promising live rainforest dome. |
| chapultepec-zoo | minor | partial | hybrid | Pandas and core megafauna high/medium; official SEDEMA URL too generic. Soft-label subspecies; red panda uncertain. |
| childrens-aquarium-dallas | ok | audited | curated | Official site highlights sharks, cownose stingrays, loggerhead turtles — solid three-stop route. Secondary reef species medium. |
| childrens-museum-perot | major | partial | curated | Drop Imaginarium and Woven Wonders leakage. Prefer real Perot anchors: Discover the Dinosaurs, Sports Hall, toddler/outdoor play. Consider a |
| cincinnati-zoo | major | audited | curated | Hippo Cove, gorilla, cheetah verified. Elephants are Asian not African — fix label. Strong curated print list possible. |
| cleveland-metroparks-zoo | major | audited | curated | Gorilla, African elephant, cheetah verified. Fix tiger→Amur, giraffe→Masai, tortoise→Aldabra; Nile hippo unclear. |
| columbus-zoo | critical | audited | curated | Official list: gorilla, giraffe, zebra, sharks/rays/turtles verified. Fix Asian not African elephant, Amur not Sumatran tiger, Humboldt not  |
| copenhagen-zoo | minor | partial | hybrid | Major European zoo with strong elephant/giraffe/lion confidence; English species inventory not fully extracted — partial. |
| dallas-arboretum | major | audited | curated | Outdoor + Children's Adventure Garden are real. Drop Makery/Imaginarium/Woven Wonders children's-museum leakage entirely. |
| dallas-world-aquarium | major | audited | curated | Sloth Forest and aquarium icons strong; replace Asian small-clawed otter with giant otter; soft-label sloth species (three-toed primary). |

## Critical slugs

- adelaide-zoo
- albuquerque-biopark
- auckland-zoo
- austin-zoo
- bangalore-bannerghatta
- cairo-zoo
- calgary-zoo
- columbus-zoo

## Major slugs

- air-and-space
- al-ain-zoo
- amnh
- antwerp-zoo
- aquarium-of-the-pacific
- arizona-science-center
- artis-zoo
- athens-attica-zoo
- bogota-zoo
- carnegie-natural-history
- childrens-museum-perot
- cincinnati-zoo
- cleveland-metroparks-zoo
- dallas-arboretum
- dallas-world-aquarium

---

# Presence audit SUMMARY — batches 06 & 07

**Audited at:** 2026-08-08  
**Venues:** 32 (batch_06=18, batch_07=14)  
**Output:** `static/field-pack/data/audits/results/{slug}.json`  

## Severity tallies

- **critical:** 7
- **major:** 13
- **minor:** 8
- **ok:** 4

## Critical (must fix before print)

### `san-antonio-zoo` — San Antonio Zoo
- **conf recommended:** partial · **mode:** curated
- **summary:** CRITICAL: elephants still on print list but left 2023. Hippos, Congo Falls gorillas, giraffes verified icons.
- **do_not_list (1):** African elephant (african-elephant)
- **absent on list:** African elephant

### `shedd-aquarium` — Shedd Aquarium
- **conf recommended:** audited · **mode:** curated
- **summary:** CRITICAL labels: African penguin and Asian small-clawed otter wrong. Sharks/jellies/turtles/seahorses/stars/GPO verified. Add beluga/sea otter.
- **do_not_list (2):** African penguin (african-penguin); Asian small-clawed otter (asian-small-clawed-otter)
- **absent on list:** African penguin, Asian small-clawed otter

### `singapore-night-safari` — Night Safari
- **conf recommended:** audited · **mode:** curated
- **summary:** CRITICAL: day-zoo template. Official: Asian elephant, Asian lion, white tiger, pangolin, otter, tapir, Tassie devil — not giraffe/chimp/zebra/red panda/African labels.
- **do_not_list (8):** African elephant (african-elephant); African lion (african-lion); Sumatran tiger (sumatran-tiger); Red panda (red-panda); Zebra (zebra); Giraffe (reticulated-giraffe); Chimpanzee (chimpanzee); Ring-tailed lemur (ring-tailed-lemur)
- **absent on list:** Sumatran tiger, African elephant, Red panda, Zebra, African lion, Reticulated giraffe, Chimpanzee, Ring-tailed lemur

### `stockholm-skansen` — Skansen
- **conf recommended:** audited · **mode:** curated
- **summary:** CRITICAL: almost entire animal pack wrong. Skansen = Nordic animals (bear, wolf, moose, lynx, reindeer) + open-air museum.
- **do_not_list (10):** african-lion (african-lion); sumatran-tiger (sumatran-tiger); reticulated-giraffe (reticulated-giraffe); african-elephant (african-elephant); western-lowland-gorilla (western-lowland-gorilla); african-penguin (african-penguin); chimpanzee (chimpanzee); zebra (zebra)
- **absent on list:** Red panda, African lion, Sumatran tiger, Reticulated giraffe, African elephant, Western lowland gorilla, African penguin, Chimpanzee, Zebra, Asian small-clawed otter

### `toronto-zoo` — Toronto Zoo
- **conf recommended:** audited · **mode:** curated
- **summary:** CRITICAL: African elephant and giant panda still on print list but ABSENT. Tiger should be Amur not Sumatran. Giraffe is Masai. Gorillas, lions, cheetahs, hippos, penguins solid.
- **do_not_list (4):** African elephant (african-elephant); Giant panda (giant-panda); Sumatran tiger (sumatran-tiger); Chimpanzee (chimpanzee)
- **absent on list:** African elephant, Sumatran tiger, Giant panda

### `wellington-zoo` — Wellington Zoo
- **conf recommended:** audited · **mode:** curated
- **summary:** CRITICAL: African elephant, hippo, gorilla, penguin, tortoise on list but absent/unconfirmed. Tigers, chimps, lions, giraffes, red pandas, otters verified. Add sun bear.
- **do_not_list (5):** African elephant (african-elephant); Nile hippo (nile-hippo); Western lowland gorilla (western-lowland-gorilla); African penguin (african-penguin); Galápagos tortoise (galapagos-tortoise)
- **absent on list:** Western lowland gorilla, African elephant, African penguin, Nile hippo, Galápagos tortoise

### `woodland-park-zoo` — Woodland Park Zoo
- **conf recommended:** audited · **mode:** curated
- **summary:** CRITICAL: elephants and hippos absent but listed. African penguin wrong (Humboldt). Tiger likely Malayan. Gorillas, giraffes, lions verified.
- **do_not_list (5):** African elephant (african-elephant); Nile hippo (nile-hippo); African penguin (african-penguin); Cheetah (cheetah); Galápagos tortoise (galapagos-tortoise)
- **absent on list:** African elephant, African penguin, Nile hippo, Galápagos tortoise

## Major

- **`rio-zoo`** (partial): Template generic zoo pack on BioParque. Prefer South American icons; many African megafauna items unconfirmed.
- **`santiago-zoo`** (partial): Hill/views are real. African megafauna pack largely unconfirmed — wonder mode until species map audited.
- **`sao-paulo-zoo`** (partial): Large Brazilian flagship; sloth/regional safer than unconfirmed pandas/otters. Medium on classic megafauna.
- **`seattle-aquarium`** (partial): MAJOR: Asian small-clawed otter wrong species. Icons should be sea otter, harbor seal, octopus, local fish.
- **`seoul-zoo`** (partial): Large municipal zoo; red panda higher confidence. Full species audit needs animals directory.
- **`singapore-zoo`** (audited): Orangutans, Asian elephants (mislabeled African), Malayan tigers, giraffes, otters, lions verified. Drop gorilla until confirmed.
- **`st-louis-zoo`** (partial): MAJOR: African elephant label wrong (Asian). Hippos, giraffes, lions, apes solid.
- **`tampa-zoo`** (partial): Elephants verified. MAJOR gap: manatees (and Florida panther) missing despite being venue identity.
- **`taronga-zoo`** (audited): Koala, tiger, gorilla, giraffe, lion, chimp, zebra, red panda, lemur verified. CRITICAL: African penguin wrong (Little penguin). Elephants gone 2025 (not in list — keep out). Prefe
- **`vancouver-aquarium`** (partial): MAJOR: Asian small-clawed otter wrong — sea otters are the icon. Confirm sea turtle still on exhibit. PNW + tropics mix otherwise plausible.
- **`waikiki-aquarium`** (partial): MAJOR: otters absent; Hawaiian monk seal missing from pack. Tiny reef aquarium — drop freshwater template. Duration likely 1–2h not half day.
- **`warsaw-zoo`** (partial): Classic large European zoo template mostly plausible at medium/high. Needs official PL animal list for audited.
- **`zurich-zoo`** (partial): MAJOR: African elephant wrong (Asian at Kaeng Krachan). Masoala is the real icon. Gorillas/savanna high. Soft-label hippo.

## Minor / OK

- **`rome-bioparco`** [minor/partial]: Core African megafauna and gorillas look solid for Bioparco; soft-label tiger subspecies. Otter/red panda still template.
- **`san-diego-zoo`** [minor/audited]: Pandas, koalas, elephants, gorillas, lions, red pandas verified. Soft-label giraffe (Masai) and tiger subspecies.
- **`shanghai-ocean-aquarium`** [minor/partial]: Tropical template mostly plausible for mega-aquarium; elevate freshwater/Chinese species. Otter medium.
- **`smithsonian-natural-history`** [minor/partial]: Dinosaur and mammal halls solid. Soft-label Ocean Hall. Avoid implying full aquarium or planetarium.
- **`taipei-zoo`** [minor/partial]: Pandas/red pandas high confidence as icons. Rest medium/template until full animal directory audited.
- **`two-oceans-aquarium`** [minor/partial]: African penguin + predators are the right icons for Cape Town waterfront aquarium. Soft-pedal generic tropical template.
- **`ueno-zoo`** [minor/audited]: Giant pandas correctly absent from items (left Jan 2026). Red panda verified; gorilla/tiger/giraffe/flamingo/kids zoo high. Never re-add gia
- **`virginia-aquarium`** [minor/partial]: Sharks, sea turtles, rays are right icons. Soft-check otter species. Outdoor aviary/boardwalk underrepresented.
- **`san-diego-safari-park`** [ok/audited]: Official animals hub confirms elephant, giraffe, lion, cheetah, gorilla, Sumatran tiger, zebra. Strong audited list.
- **`thinkery`** [ok/partial]: Children's museum zone pack is appropriate; not species-critical. Confirm named zones against current map before audited.
- **`union-station-kc-science`** [ok/partial]: Science museum zone pack OK at hybrid level. Not species-critical. Confirm space/dino labels vs current map.
- **`vienna-zoo`** [ok/audited]: Giant pandas, African elephants, orangutans verified icons at world's oldest zoo. Soft-label tiger subspecies. Strong audited core.

## Full table

| slug | severity | conf | mode | items | absent | dnl |
|---|---|---|---|---:|---:|---:|
| san-antonio-zoo | critical | partial | curated | 12 | 1 | 1 |
| shedd-aquarium | critical | audited | curated | 10 | 2 | 2 |
| singapore-night-safari | critical | audited | curated | 10 | 8 | 8 |
| stockholm-skansen | critical | audited | curated | 14 | 10 | 10 |
| toronto-zoo | critical | audited | curated | 12 | 3 | 4 |
| wellington-zoo | critical | audited | curated | 12 | 5 | 5 |
| woodland-park-zoo | critical | audited | curated | 13 | 4 | 5 |
| rio-zoo | major | partial | wonder | 13 | 0 | 4 |
| santiago-zoo | major | partial | wonder | 13 | 0 | 4 |
| sao-paulo-zoo | major | partial | hybrid | 13 | 0 | 1 |
| seattle-aquarium | major | partial | curated | 12 | 1 | 1 |
| seoul-zoo | major | partial | hybrid | 12 | 0 | 2 |
| singapore-zoo | major | audited | curated | 12 | 1 | 2 |
| st-louis-zoo | major | partial | curated | 10 | 1 | 1 |
| tampa-zoo | major | partial | curated | 13 | 0 | 0 |
| taronga-zoo | major | audited | curated | 12 | 1 | 3 |
| vancouver-aquarium | major | partial | curated | 12 | 1 | 1 |
| waikiki-aquarium | major | partial | curated | 12 | 2 | 2 |
| warsaw-zoo | major | partial | hybrid | 12 | 0 | 0 |
| zurich-zoo | major | partial | curated | 13 | 1 | 2 |
| rome-bioparco | minor | partial | hybrid | 12 | 0 | 0 |
| san-diego-zoo | minor | audited | curated | 10 | 0 | 0 |
| shanghai-ocean-aquarium | minor | partial | hybrid | 12 | 0 | 0 |
| smithsonian-natural-history | minor | partial | hybrid | 8 | 0 | 0 |
| taipei-zoo | minor | partial | hybrid | 12 | 0 | 0 |
| two-oceans-aquarium | minor | partial | curated | 12 | 0 | 0 |
| ueno-zoo | minor | audited | curated | 12 | 0 | 2 |
| virginia-aquarium | minor | partial | hybrid | 12 | 0 | 0 |
| san-diego-safari-park | ok | audited | curated | 10 | 0 | 0 |
| thinkery | ok | partial | hybrid | 8 | 0 | 0 |
| union-station-kc-science | ok | partial | hybrid | 8 | 0 | 0 |
| vienna-zoo | ok | audited | curated | 13 | 0 | 0 |

## Cross-cutting failure modes

1. **Wrong elephant species/catalog** — African stamped where Asian only (Singapore Zoo/Night Safari, St. Louis, Zurich) or **elephants absent** (San Antonio, Toronto, Wellington, Woodland Park, Taronga 2025).
2. **Wrong otter** — Asian small-clawed stamped on sea-otter aquariums (Shedd, Seattle, Vancouver, Waikiki).
3. **Wrong penguin species** — African penguin stamped on Humboldt/Magellanic/rockhopper/little penguin venues (Shedd, Woodland Park, Taronga).
4. **Tiger subspecies** — Sumatran default vs Malayan/Amur/Siberian (Singapore, Toronto, San Diego Zoo, Vienna).
5. **Whole-pack wrong venue type** — Skansen Nordic open-air museum; Night Safari nocturnal list ≠ day-zoo template.
6. **Missing signature icons** — ZooTampa manatees; Waikiki Hawaiian monk seal; Shedd beluga/sea otter.
7. **Encoding/address** — São Paulo name OK in JSON; Shedd address DuSable Lake Shore Drive; region fields often hold country names.

## Notes

- Audit JSON only — **live venue JSON/HTML not modified**.
- Presence values never invented as verified without an official or strong secondary source.
- `list_confidence_recommended: audited` means enough sources to gate print; still apply `do_not_list` and soft labels.

# Presence audit SUMMARY — batches 04–05 (2026-08-08)
Written: **36** venue audit files → `static/field-pack/data/audits/results/{slug}.json`
Severity: critical=9 major=17 minor=9 ok=1

| slug | severity | confidence | absent | verified+high | do_not_list | notes |
|------|----------|------------|--------|---------------|-------------|-------|
| melbourne-zoo | critical | audited | 5 | 9 | 5 | Elephants moved to Werribee 2025; African elephant false |
| memphis-zoo | critical | audited | 1 | 12 | 1 | Giant pandas gone 2023; still on route |
| miami-zoo | major | audited | 1 | 9 | 1 | Nile hippo→pygmy; core icons OK |
| milan-aquarium | major | partial | 1 | 1 | 1 | Template pack on small civic aquarium |
| milwaukee-zoo | major | audited | 2 | 6 | 2 | Wrong penguin species; core Africa OK |
| minnesota-zoo | critical | audited | 8 | 2 | 11 | No elephant/giraffe/lion/zebra; Amur≠Sumatran tiger |
| monterey-bay-aquarium | major | audited | 1 | 7 | 1 | ASC otter catalog used for sea otters |
| montreal-biodome | major | audited | 2 | 5 | 2 | Generic sci halls vs ecosystems |
| moscow-zoo | major | partial | 0 | 3 | 0 | Thin English verification |
| mumbai-byculla-zoo | critical | partial | 7 | 1 | 8 | Heavy tropical template leakage |
| munich-zoo | minor | partial | 0 | 6 | 0 | Hellabrunn partial |
| museum-of-science-boston | major | partial | 2 | 4 | 1 | No shuttle orbiter; generic CM labels |
| museum-of-science-industry-chi | critical | audited | 4 | 2 | 4 | Misses U-505/Science Storms; generic halls |
| nairobi-safari-walk | critical | partial | 4 | 5 | 5 | Sumatran tiger/penguin/gorilla leakage |
| nashville-adventure-science | major | partial | 2 | 4 | 1 | Shuttle/Imaginarium leakage |
| nashville-zoo | major | audited | 0 | 6 | 1 | Masai≠reticulated giraffe; fillers weak |
| national-aquarium-baltimore | minor | audited | 0 | 9 | 0 | Solid aquarium list |
| national-zoo | critical | audited | 2 | 8 | 2 | Asian≠African elephant; no giraffes; pandas OK |
| new-england-aquarium | ok | audited | 0 | 8 | 0 | Myrtle/penguins/sharks solid |
| nhm-london | major | audited | 3 | 4 | 3 | No rainforest/aquarium; Earth≠space |
| north-carolina-zoo | major | audited | 4 | 5 | 7 | Asia tigers not open yet |
| omaha-henry-doorly | minor | audited | 0 | 9 | 0 | Strong top-tier zoo |
| oregon-museum-science-industry | major | audited | 2 | 4 | 1 | Blueback sub not shuttle |
| oregon-zoo | major | audited | 1 | 5 | 1 | Asian≠African elephant |
| orlando-science-center | major | partial | 2 | 4 | 1 | No shuttle; generic labels |
| osaka-aquarium | minor | partial | 0 | 7 | 1 | Whale shark icon; otter weak |
| oslo-zoo | major | partial | 1 | 6 | 4 | Kristiansand not Oslo; Siberian≠Sumatran tiger |
| paris-zoo | minor | partial | 0 | 6 | 0 | Vincennes partial |
| perot-museum | minor | audited | 1 | 4 | 1 | No rainforest dome |
| perth-zoo | critical | audited | 5 | 8 | 5 | No elephant/gorilla; little≠African penguin |
| philadelphia-zoo | critical | audited | 2 | 7 | 2 | Elephants gone 2009; Amur≠Sumatran tiger |
| phoenix-zoo | major | audited | 4 | 9 | 4 | Asian≠African elephant; no gorilla/hippo |
| pittsburgh-zoo | minor | partial | 0 | 8 | 0 | Zoo+aquarium partial |
| please-touch-museum | minor | partial | 0 | 5 | 0 | Hall names need PTM map align |
| point-defiance-zoo | major | audited | 2 | 8 | 3 | No giraffe/zebra; ASC otter OK |
| prague-zoo | minor | partial | 0 | 7 | 0 | Large zoo partial English |

## Critical slugs (do not print unaudited lists)
- `melbourne-zoo` — Elephants moved to Werribee 2025; African elephant false 
- `memphis-zoo` — Giant pandas gone 2023; still on route 
- `minnesota-zoo` — No elephant/giraffe/lion/zebra; Amur≠Sumatran tiger 
- `mumbai-byculla-zoo` — Heavy tropical template leakage 
- `museum-of-science-industry-chi` — Misses U-505/Science Storms; generic halls 
- `nairobi-safari-walk` — Sumatran tiger/penguin/gorilla leakage 
- `national-zoo` — Asian≠African elephant; no giraffes; pandas OK 
- `perth-zoo` — No elephant/gorilla; little≠African penguin 
- `philadelphia-zoo` — Elephants gone 2009; Amur≠Sumatran tiger 

## Major slugs
- `miami-zoo` — Nile hippo→pygmy; core icons OK 
- `milan-aquarium` — Template pack on small civic aquarium 
- `milwaukee-zoo` — Wrong penguin species; core Africa OK 
- `monterey-bay-aquarium` — ASC otter catalog used for sea otters 
- `montreal-biodome` — Generic sci halls vs ecosystems 
- `moscow-zoo` — Thin English verification 
- `museum-of-science-boston` — No shuttle orbiter; generic CM labels 
- `nashville-adventure-science` — Shuttle/Imaginarium leakage 
- `nashville-zoo` — Masai≠reticulated giraffe; fillers weak 
- `nhm-london` — No rainforest/aquarium; Earth≠space 
- `north-carolina-zoo` — Asia tigers not open yet 
- `oregon-museum-science-industry` — Blueback sub not shuttle 
- `oregon-zoo` — Asian≠African elephant 
- `orlando-science-center` — No shuttle; generic labels 
- `oslo-zoo` — Kristiansand not Oslo; Siberian≠Sumatran tiger 
- `phoenix-zoo` — Asian≠African elephant; no gorilla/hippo 
- `point-defiance-zoo` — No giraffe/zebra; ASC otter OK 
