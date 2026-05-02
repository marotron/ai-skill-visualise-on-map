# ai-skill-visualise-on-map

Skill for visualising geographic or region-based results on an interactive map (choropleth, markers, or heatmap). Use when there is location data, places, regions, coordinates, or results that should be shown on a map.

## Structure

Skills are provided for two platforms in separate folders:

| Folder      | Platform   | Description |
|------------|------------|-------------|
| `perplexity/` | Perplexity | Skill and assets for Perplexity AI |
| `cursor/`     | Cursor     | Skill and assets for Cursor IDE   |

Each folder contains the platform-specific skill definition and any related files. Do not mix assets between the two; keep changes in the appropriate folder when updating.

### Cursor layout

| Path | Purpose |
|------|---------|
| `cursor/SKILL.md` | Agent skill instructions |
| `cursor/scripts/visualise_on_map.py` | Folium export (choropleth / markers / heatmap) |
| `cursor/data/uk_nuts1.geojson` | Optional bundled UK NUTS1 boundaries for `--preset uk` |
| `cursor/examples.md` | Extra examples |

Install by copying the **`cursor/`** tree into `~/.cursor/skills/visualise_on_map/` (or symlink), then create the venv as described in `SKILL.md`.

## Usage

- **Perplexity**: Use the contents of `perplexity/` according to Perplexity’s skill/project documentation. **Note:** Adding this as a skill in Perplexity (e.g. under Computer → Skills) requires a **Perplexity Max** subscription (~$200/month).
- **Cursor**: Use the contents of `cursor/` (e.g. copy into `.cursor/skills/` or follow Cursor’s skill setup).

## License

See repository license file if present.
