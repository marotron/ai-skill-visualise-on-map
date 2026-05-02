# Bundled map data

## `uk_nuts1.geojson`

- **What:** 12 NUTS 2021 level-1 polygons for the United Kingdom (GB + Northern Ireland), derived from the Eurostat Nuts2json distribution.
- **Join column:** each feature has `properties.id` (e.g. `UKC` … `UKN`) and **`properties.na`** (English region name, e.g. `North East (England)`, `Scotland`). Choropleth CSV column **`region`** must match **`na`** exactly.
- **Source:** [Eurostat Nuts2json](https://eurostat.github.io/Nuts2json/) — GeoJSON, 2021, 20M, EPSG:4326, `nutsrg_1.json`, filtered to features whose `id` starts with `UK`.
- **Update:** To refresh, download the same upstream file and re-run the filter (see repository maintenance notes or `SKILL.md`).
