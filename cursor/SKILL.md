---
name: visualise-results-on-map
description: Visualise geographic or region-based results on an interactive map (choropleth, markers, or heatmap). Use when the user or context includes location data, places, regions, coordinates, or Perplexity-style results that should be shown on a map.
---

# Visualise Results on Map

## Installation (one-time)

**Recommended: venv inside the skill folder**  
One install, works from any project. The script is run with the skill’s Python so you never need to activate the venv or install map deps per project.

```bash
cd ~/.cursor/skills/visualise_on_map
python3 -m venv .venv
.venv/bin/pip install -r scripts/requirements.txt
```

Use this to run the script (from any directory). **`SKILL_ROOT`** means the folder that contains `SKILL.md` (when installed: `~/.cursor/skills/visualise_on_map`; in this repo: `cursor/`).

```bash
$SKILL_ROOT/.venv/bin/python $SKILL_ROOT/scripts/visualise_on_map.py -i data.json -o map.html
```

**Alternative: project venv or global**  
- In a **project venv**: activate it, then `pip install -r $SKILL_ROOT/scripts/requirements.txt`; run with `python .../visualise_on_map.py` (same `python` as that venv).  
- **Global**: run the same `pip install -r ...` with no venv active; then `python` is system/user Python.

Requires: `folium`, `pandas`. For region/choropleth maps also `geopandas`.

## Basemap and opening HTML locally

The map uses **CartoDB Positron** tiles by default (not raw OpenStreetMap raster tiles). That avoids **403 “Access blocked”** overlays when opening the exported HTML as **`file://`** — volunteer OSM tile servers often reject requests without an acceptable `Referer` ([policy](https://osm.wiki/Blocked)).

---

## How to use this skill

- **In Cursor**: Ask in natural language, e.g. “Show these on a map”, “Put these locations on a map”, or “Visualise this data on a map.” When your question implies showing locations or results on a map, the agent will use this skill: it will help you turn your data (or search results you paste) into a JSON/CSV, run the script, and tell you to open the generated HTML map.
- **Data first**: The skill **visualises** data it is given. It does not fetch listings or search the web. Whatever you want to map—places, events, properties, sites, regions, coordinates—get the list or dataset first, then in Cursor ask to “show these on a map” or “visualise these on a map” and paste the list (place names, regions, addresses, or lat/lon). The agent will build the input file, geocode if needed, run the script, and you open the resulting HTML in your browser.

Use this skill when you need to **visualise geographic or region-based data** (e.g. from search results, a list of places, regional stats, or lat/lon points) as an interactive map.

## When to use

- User asks to "put results on a map", "show on map", "visualise on a map", or "map these" (locations, points, events, properties, regions, etc.).
- Data includes: **regions** (e.g. voivodeships, states), **lat/lon** coordinates, or **place names** you can geocode.
- Output from tools or search (e.g. Perplexity-style answers) contains locations or regions to display.

## Data shape → map type

| Data you have | Map type | Notes |
|---------------|----------|--------|
| `region` + `value` | Choropleth | Needs a GeoJSON whose **region labels** match a property on each feature (see `--geojson-key`). |
| `lat` + `lon` (points) | Markers | Optional `name`, `value` for popups. Optional `url` or `link` for a source link in the popup. |
| `lat` + `lon` + `value` | Heatmap | Value = intensity. |

### Choropleth: matching region names

- **`--geojson-key`** tells Folium which GeoJSON property joins to your CSV column **`region`**. Examples: `feature.properties.name`, `feature.properties.na`.
- **UK official statistics** often label regions like ONS **“East”** while boundary files use **“East of England”** — the **`region`** column must match the **GeoJSON** label exactly, not the headline table shorthand.
- **Bundled UK data** uses Eurostat labels in **`properties.na`** (e.g. **“Yorkshire and the Humber”** — note **the**).

---

## Quick workflow

1. **Get data**  
   From user message, a file, or previous step: build a table with either  
   - `region` + `value`, or  
   - `lat` + `lon` (and optionally `value`, `name`).

2. **Save to JSON or CSV**  
   Example JSON (points with optional label, value, and source link):
   ```json
   [
     { "name": "Location A", "lat": 52.23, "lon": 21.01, "value": 10 },
     { "name": "Location B", "lat": 50.06, "lon": 19.94, "url": "https://example.com/source" }
   ]
   ```
   The `name` field is any label (place, event, site, etc.). Include a `url` or `link` column to show a **“View listing →”** (or source) link in each marker popup. Example CSV: `region,value` or `lat,lon,value` or `name,lat,lon` or `name,lat,lon,url`.

3. **Run the script**  
   From any project. Prefer the skill’s venv (if you installed there):
   ```bash
   ~/.cursor/skills/visualise_on_map/.venv/bin/python ~/.cursor/skills/visualise_on_map/scripts/visualise_on_map.py --input data.json --output map.html
   ```
   Or with CSV:
   ```bash
   ~/.cursor/skills/visualise_on_map/.venv/bin/python ~/.cursor/skills/visualise_on_map/scripts/visualise_on_map.py -i points.csv -o map.html
   ```
   (If you use a project venv or global install, use `python` instead of the long path.)

4. **UK choropleth (one flag)**  
   If regions are UK NUTS1 and values match bundled boundary labels (`data/uk_nuts1.geojson`, Eurostat **`na`**):
   ```bash
   ~/.cursor/skills/visualise_on_map/.venv/bin/python ~/.cursor/skills/visualise_on_map/scripts/visualise_on_map.py \
     --preset uk -i regions.csv -o map.html -t "Legend title" -n "Source and methodology note"
   ```
   `--preset uk` sets **`--geojson`** to `$SKILL_ROOT/data/uk_nuts1.geojson` and **`--geojson-key`** to `feature.properties.na` unless you override with `-g` / `-k` or **`GEOJSON_KEY`** in the environment.

5. **Choropleth (generic)**  
   If you have regions + values and any GeoJSON file:
   ```bash
   ~/.cursor/skills/visualise_on_map/.venv/bin/python ~/.cursor/skills/visualise_on_map/scripts/visualise_on_map.py \
     -i regions.csv -o map.html --geojson path/to/regions.geojson -k feature.properties.name
   ```

6. **Open the result**  
   Open the map automatically when possible so the user sees it right away:
   - **macOS**: `open <output_path>` (e.g. `open map.html`)
   - **Linux**: `xdg-open <output_path>`
   - **Windows**: `start <output_path>`
   Use the same path you passed to `--output` / `-o`.
   - **Sandbox**: Cursor’s terminal sandbox can block `open` (e.g. macOS error -10661). When running the open command, request **full permissions** (e.g. `required_permissions: ["all"]`) so it runs outside the sandbox and Launch Services can start the browser. If the open command still fails, tell the user to open the HTML file in their browser manually.

## Script reference

- **Path**: `$SKILL_ROOT/scripts/visualise_on_map.py`  
  **Run with (skill venv)**: `$SKILL_ROOT/.venv/bin/python` + script path
- **Dependencies**: `folium`, `pandas`. Choropleth also uses `geopandas` and a GeoJSON file.
- **Args**: `--input` / `-i`, `--output` / `-o`, `--geojson` / `-g`, `--geojson-key` / `-k`, **`--preset uk`**, `--legend-title` / `-t`, `--legend-note` / `-n`.
- **Env**: `DATA_PATH`, `OUTPUT_PATH`, `GEOJSON_PATH`, `GEOJSON_KEY`, `LEGEND_TITLE`, `LEGEND_NOTE` can replace args where supported.

If no `--input` is given, the script uses built-in sample data and writes `universal_map.html`.

- **Source links in popups**: If your data has a `url` or `link` column, marker popups will show the label plus a “View listing →” link that opens in a new tab. The script uses an iframe so the link is rendered as HTML correctly.
- For more examples (point list, choropleth, heatmap, **UK**), see [examples.md](examples.md).

## Geocoding

If the user only has **place names** or addresses (no lat/lon), geocode them first to get `lat`/`lon` (e.g. with a geocoding API or library), then pass the resulting CSV/JSON into the script as above.

## Optional: PNG export

The script outputs HTML only. For PNG, the user can open the HTML in a browser and screenshot, or use something like `imgkit`/`selenium` in a separate step; do not add this to the core script unless requested.
