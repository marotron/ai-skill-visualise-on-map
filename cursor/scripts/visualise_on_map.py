#!/usr/bin/env python3
"""
Visualise geographic or region-based results on an interactive map.
Supports: choropleth (regions), markers (points), heatmap (lat/lon + value).
Usage:
  python visualise_on_map.py [--input data.json|data.csv] [--output map.html]
  Or set DATA_PATH / OUTPUT_PATH env vars.
"""
import argparse
import json
import os
import sys

import pandas as pd

# Optional: geopandas for choropleth; folium for all map types
try:
    import folium
    from folium.plugins import MarkerCluster
    from branca.element import IFrame
except ImportError:
    print("Install folium: pip install folium", file=sys.stderr)
    sys.exit(1)

try:
    import geopandas as gpd
except ImportError:
    gpd = None

# ---------------------------------------------------------------------------
# USER DATA - replace or pass via --input (JSON/CSV)
# Any geographic data: places, events, sites, regions, etc.
# JSON: list of objects with keys e.g. region, value, lat, lon, name
# CSV: columns region, value and/or lat, lon, name (name = any label for popup)
# ---------------------------------------------------------------------------
DEFAULT_DATA = {
    "region": ["Mazowieckie", "Śląskie", "Małopolskie"],
    "value": [10, 20, 30],
    "lat": [52.0, 50.5, 50.0],
    "lon": [21.0, 19.0, 20.0],
}


def load_data(path: str) -> pd.DataFrame:
    path = path.strip()
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Data file not found: {path}")
    if path.lower().endswith(".json"):
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)
        if isinstance(raw, list):
            return pd.DataFrame(raw)
        return pd.DataFrame([raw])
    return pd.read_csv(path)


def get_center_and_zoom(df: pd.DataFrame) -> tuple:
    if "lat" in df.columns and "lon" in df.columns:
        lat, lon = df["lat"].mean(), df["lon"].mean()
        return [lat, lon], 6
    return [52.0, 20.0], 6  # default Poland


def build_map(df: pd.DataFrame, geo_geojson: str | None, output_path: str) -> None:
    location, zoom = get_center_and_zoom(df)
    m = folium.Map(location=location, zoom_start=zoom)

    if "region" in df.columns and "value" in df.columns and geo_geojson and os.path.isfile(geo_geojson):
        # Choropleth: region-based shading
        folium.Choropleth(
            geo_data=geo_geojson,
            data=df,
            columns=["region", "value"],
            key_on="feature.properties.name",
            fill_color="YlOrRd",
            fill_opacity=0.7,
            legend_name="Value",
        ).add_to(m)
    elif "lat" in df.columns and "lon" in df.columns:
        if "value" in df.columns and df["value"].dtype in (pd.Int64Dtype(), "int64", "float64"):
            # Heatmap: lat, lon, value
            heat_data = [
                [row["lat"], row["lon"], row["value"]] for _, row in df.iterrows()
            ]
            folium.HeatMap(heat_data).add_to(m)
        else:
            # Markers: point layer with optional popup (wider popup for readability)
            marker_cluster = MarkerCluster().add_to(m)
            name_col = "name" if "name" in df.columns else df.columns[0]
            link_col = "url" if "url" in df.columns else "link" if "link" in df.columns else None
            for _, row in df.iterrows():
                name_val = row.get(name_col, "")
                value_val = row.get("value", "")
                text_part = f"{name_val}: {value_val}".strip(": ") if value_val else name_val
                if link_col and pd.notna(row.get(link_col)) and row.get(link_col):
                    link_url = str(row[link_col]).strip()
                    # Escape for HTML attribute to avoid injection
                    link_url_esc = link_url.replace("&", "&amp;").replace('"', "&quot;")
                    text_esc = (text_part or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                    html = f'<div style="font-family:sans-serif;font-size:13px;max-width:320px;line-height:1.4;">{text_esc}<br><a href="{link_url_esc}" target="_blank" rel="noopener">View listing →</a></div>'
                    iframe = IFrame(html=html, width=340, height=100)
                    popup = folium.Popup(iframe, max_width=360)
                else:
                    popup = folium.Popup(text_part or " ", max_width=360)
                folium.Marker(
                    [row["lat"], row["lon"]],
                    popup=popup,
                ).add_to(marker_cluster)
    else:
        print("Need columns: (region + value) or (lat + lon) or (lat + lon + value)", file=sys.stderr)
        sys.exit(1)

    m.save(output_path)
    print(f"Map saved: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Visualise results on a map")
    parser.add_argument("--input", "-i", default=os.environ.get("DATA_PATH"), help="Input JSON or CSV path")
    parser.add_argument("--output", "-o", default=os.environ.get("OUTPUT_PATH", "universal_map.html"), help="Output HTML path")
    parser.add_argument("--geojson", "-g", default=os.environ.get("GEOJSON_PATH"), help="GeoJSON for choropleth (e.g. poland.geojson)")
    args = parser.parse_args()

    if args.input:
        df = load_data(args.input)
    else:
        df = pd.DataFrame(DEFAULT_DATA)

    build_map(df, args.geojson, args.output)


if __name__ == "__main__":
    main()
