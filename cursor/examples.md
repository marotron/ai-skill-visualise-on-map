# Examples: Visualise results on map

The skill works with **any geographic data**: places, events, properties, sites, regions, or raw lat/lon. You provide the data; the script visualises it.

## Example: “Show these on a map”

1. **Get your list or dataset** (the skill does not fetch data). For example:
   - A list of places (cities, addresses, landmarks),
   - Events or venues (meetups, offices, stores),
   - Properties, sites, or any points with coordinates or names.
2. **In Cursor**, say e.g.: “Put these on a map: [your list]” or “Visualise this data on a map” and paste the list or data. The agent will:
   - Geocode place names to lat/lon if needed,
   - Build a JSON/CSV and run the map script,
   - Tell you to open the generated HTML file in your browser.
3. **Open the HTML file** in Chrome/Firefox/Safari to see the interactive map.

To show **extra info** on the map (e.g. in popups), provide data with `name`, `lat`, `lon`, and optionally `value` (e.g. price, count, score). To add **source links** in popups (e.g. “View listing →”), include a `url` or `link` column in your JSON/CSV; the script will render them as clickable links inside an iframe so HTML is displayed correctly.

---

## Example 1: List of points (markers)

User says: "Show these on a map: Warsaw, Krakow, Wroclaw, Poznan" (or any list of places, events, sites, etc.).

1. Build `locations.json` (or any filename):
```json
[
  { "name": "Warsaw", "lat": 52.23, "lon": 21.01 },
  { "name": "Krakow", "lat": 50.06, "lon": 19.94 },
  { "name": "Wroclaw", "lat": 51.11, "lon": 17.04 },
  { "name": "Poznan", "lat": 52.41, "lon": 16.93 }
]
```
2. Run:
```bash
~/.cursor/skills/visualise_on_map/.venv/bin/python ~/.cursor/skills/visualise_on_map/scripts/visualise_on_map.py -i locations.json -o map.html
```
3. User opens the output HTML file.

## Example 2: Regional values (choropleth)

User has a CSV of Polish voivodeships and a metric:

| region      | value |
|------------|-------|
| Mazowieckie | 100   |
| Małopolskie | 80    |
| Śląskie     | 75    |

1. Save as `regions.csv`.
2. Ensure a GeoJSON exists (e.g. `poland.geojson`) with `feature.properties.name` matching `region`.
3. Run:
```bash
~/.cursor/skills/visualise_on_map/.venv/bin/python ~/.cursor/skills/visualise_on_map/scripts/visualise_on_map.py -i regions.csv -o regions_map.html --geojson poland.geojson
```

## Example 3: Points with intensity (heatmap)

Data: lat, lon, value (e.g. count, intensity, or any numeric metric per point).

```json
[
  { "lat": 52.23, "lon": 21.01, "value": 5 },
  { "lat": 50.06, "lon": 19.94, "value": 12 }
]
```

Same as Example 1 but with a `value` field; the script will choose the heatmap layer automatically.
