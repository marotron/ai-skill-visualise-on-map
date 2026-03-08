# ai-skill-visualise-on-map

Skill for visualising geographic or region-based results on an interactive map (choropleth, markers, or heatmap). Use when there is location data, places, regions, coordinates, or results that should be shown on a map.

## Structure

Skills are provided for two platforms in separate folders:

| Folder      | Platform   | Description |
|------------|------------|-------------|
| `perplexity/` | Perplexity | Skill and assets for Perplexity AI |
| `cursor/`     | Cursor     | Skill and assets for Cursor IDE   |

Each folder contains the platform-specific skill definition and any related files. Do not mix assets between the two; keep changes in the appropriate folder when updating.

## Usage

- **Perplexity**: Use the contents of `perplexity/` according to Perplexity’s skill/project documentation. **Note:** Adding this as a skill in Perplexity (e.g. under Computer → Skills) requires a **Perplexity Max** subscription (~$200/month).
- **Cursor**: Use the contents of `cursor/` (e.g. copy into `.cursor/skills/` or follow Cursor’s skill setup).

## License

See repository license file if present.
