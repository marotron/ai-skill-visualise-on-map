# Perplexity skill: Map-ready location results

Add this to your **Perplexity profile** (e.g. Goals or custom instructions) or paste it at the start of a query when you want results you can later show on a map in Cursor.

---

## Instruction text (copy below)

**When my question returns location-based results** (e.g. properties, restaurants, events, places, points of interest) **or I ask to "show on a map" or "put on a map":**

1. **Answer as usual** with a clear summary and source links.
2. **Also output the results in map-ready format** so I can visualise them on an interactive map in Cursor:
   - Prefer **latitude and longitude** (`lat`, `lon`) for each item when you can infer or look them up; otherwise use **place name or address** (I can geocode later).
   - For each location include: `name` (short label, e.g. "ul. X – 279 000 PLN, 2 pokoje, 55 m²"), and if there is a source URL for that result, include `url` (or `link`).
3. **Provide a JSON array** in a fenced code block (language `json`) with one object per location, e.g.:
   ```json
   [
     { "name": "Place or listing description", "lat": 52.23, "lon": 21.01, "url": "https://source.com/item/1" },
     { "name": "Second place", "lat": 50.06, "lon": 19.94, "url": "https://source.com/item/2" }
   ]
   ```
   If you don't have coordinates, use `"name": "Address or place name"` only (no `lat`/`lon`); the user can geocode in Cursor.
4. **Add one short line** after the JSON:  
   *"To see these on an interactive map: copy the JSON above into Cursor and ask: **Show these on a map**."*

**Data shape reminder:**  
- Points (markers): `name`, `lat`, `lon`, optional `url` or `link`.  
- Regions with a value (choropleth): `region`, `value` (needs a GeoJSON in Cursor).

---

## Short version (for profile / character limit)

When my answer lists **places, properties, or locations**, also output a **JSON array** in a code block: each object has `name`, and preferably `lat`, `lon`, and `url` (source link). Example: `[{"name":"Place A","lat":52.23,"lon":21.01,"url":"https://..."}]`. Add: *"Copy this JSON into Cursor and ask: Show these on a map."*

---

## How to use in Perplexity

- **Profile**: In Perplexity → Settings / Profile, paste the **Short version** into Goals or any custom-instructions field.
- **Per query**: When you ask something like "cheapest properties in Olsztyn" or "best cafes in Warsaw", you can start your message with:  
  *"When you list results, also give me a JSON array (name, lat, lon, url) so I can show them on a map in Cursor."*
- **After the fact**: If Perplexity already gave you a list without JSON, reply:  
  *"Put these results in map-ready JSON format: name, lat, lon, url for each item."*

The resulting JSON can be saved as a `.json` file and used with the **Cursor skill** `visualise_on_map` (script: `visualise_on_map.py -i data.json -o map.html`) to generate an interactive HTML map with clickable markers and source links.
