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
    from folium.utilities import JsCode
    from branca.element import IFrame, MacroElement, Template
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


def _geojson_key_to_prop(geojson_key: str) -> str:
    """From 'feature.properties.WD13NM' return 'WD13NM'."""
    parts = geojson_key.split(".")
    return parts[-1] if parts else "name"


def _add_choropleth_popups(
    m: "folium.Map",
    df: pd.DataFrame,
    geo_geojson_path: str,
    geojson_key: str,
) -> None:
    """Add a transparent GeoJson overlay with popup (info + link) per region."""
    prop_name = _geojson_key_to_prop(geojson_key)
    with open(geo_geojson_path, encoding="utf-8") as f:
        geo_data = json.load(f)
    # Build lookup: region -> row (value, optional info, optional url/link)
    df_lookup = df.set_index("region").to_dict("index")
    info_col = "info" if "info" in df.columns else None
    link_col = "url" if "url" in df.columns else ("link" if "link" in df.columns else None)

    for feature in geo_data.get("features", []):
        props = feature.setdefault("properties", {})
        region_id = props.get(prop_name)
        if region_id is None:
            continue
        row = df_lookup.get(region_id)
        if row is None:
            continue
        value = row.get("value", "")
        info = (row.get(info_col) if info_col else None) or ""
        link = (row.get(link_col) if link_col else None) or ""
        # Escape for HTML
        safe = lambda s: (str(s) if pd.notna(s) else "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
        parts = [f"<b>{safe(region_id)}</b>", f"Value: {safe(value)}"]
        if info:
            parts.append(safe(info))
        if link:
            link_esc = str(link).strip().replace("&", "&amp;").replace('"', "&quot;")
            parts.append(f'<a href="{link_esc}" target="_blank" rel="noopener">View source →</a>')
        html = "<div style=\"font-family:sans-serif;font-size:13px;max-width:320px;line-height:1.5;\">" + "<br>".join(parts) + "</div>"
        props["_popup_html"] = html

    # Bind popup from injected _popup_html (JsCode runs in browser)
    _popup_js = JsCode(
        """
    function(feature, layer) {
        if (feature.properties && feature.properties._popup_html) {
            layer.bindPopup(feature.properties._popup_html, {maxWidth: 360});
        }
    }
    """
    )
    folium.GeoJson(
        geo_data,
        style_function=lambda _: {"fillOpacity": 0, "weight": 0},
        on_each_feature=_popup_js,
    ).add_to(m)


def get_center_and_zoom(df: pd.DataFrame, geo_geojson: str | None = None) -> tuple:
    if "lat" in df.columns and "lon" in df.columns:
        lat, lon = df["lat"].mean(), df["lon"].mean()
        return [lat, lon], 6
    if geo_geojson and os.path.isfile(geo_geojson) and gpd is not None:
        try:
            gdf = gpd.read_file(geo_geojson)
            bounds = gdf.total_bounds  # minx, miny, maxx, maxy
            lat = (bounds[1] + bounds[3]) / 2
            lon = (bounds[0] + bounds[2]) / 2
            return [lat, lon], 11
        except Exception:
            pass
    return [52.0, 20.0], 6  # default Poland


def _legend_escape(s: str) -> str:
    """Escape for HTML in legend text."""
    if not s or not isinstance(s, str):
        return ""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _add_legend_note(m: "folium.Map", title: str, note: str) -> None:
    """Add a draggable box under the legend explaining what the values mean and how they were calculated."""
    title_esc = _legend_escape(title)
    note_esc = _legend_escape(note)
    legend_html = (
        '<div id="legend-note" style="'
        "position: fixed; bottom: 50px; right: 50px; z-index: 9999; "
        "background: white; border: 1px solid #999; border-radius: 6px; "
        "padding: 10px 14px; max-width: 320px; font-family: sans-serif; "
        "font-size: 12px; line-height: 1.5; box-shadow: 0 2px 6px rgba(0,0,0,0.2);"
        '">'
        f'<div style="font-weight: bold; margin-bottom: 6px;">What the numbers mean</div>'
        f'<div style="margin-bottom: 6px;">{title_esc}</div>'
        '<div style="font-weight: bold; margin-bottom: 4px;">How the scores were calculated</div>'
        f'<div style="color: #444;">{note_esc}</div>'
        "</div>"
    )
    macro = MacroElement()
    macro._template = Template("{% macro html(this, kwargs) %}" + legend_html + "{% endmacro %}")
    m.get_root().add_child(macro)


def build_map(
    df: pd.DataFrame,
    geo_geojson: str | None,
    output_path: str,
    geojson_key: str = "feature.properties.name",
    legend_title: str | None = None,
    legend_note: str | None = None,
) -> None:
    location, zoom = get_center_and_zoom(df, geo_geojson)
    m = folium.Map(location=location, zoom_start=zoom)

    if "region" in df.columns and "value" in df.columns and geo_geojson and os.path.isfile(geo_geojson):
        # Choropleth: region-based shading (areas)
        folium.Choropleth(
            geo_data=geo_geojson,
            data=df,
            columns=["region", "value"],
            key_on=geojson_key,
            fill_color="YlOrRd",
            fill_opacity=0.7,
            legend_name=legend_title or "Value",
        ).add_to(m)
        if legend_note:
            _add_legend_note(m, legend_title or "Value", legend_note)
        # Popups: overlay transparent GeoJson with HTML popup per region (info + source link)
        _add_choropleth_popups(m, df, geo_geojson, geojson_key)
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
    parser.add_argument(
        "--geojson-key", "-k",
        default=os.environ.get("GEOJSON_KEY", "feature.properties.name"),
        help="GeoJSON property path for choropleth join (e.g. feature.properties.WD13NM for UK wards)",
    )
    parser.add_argument("--legend-title", "-t", default=os.environ.get("LEGEND_TITLE"), help="Choropleth legend title (e.g. Crime rate)")
    parser.add_argument("--legend-note", "-n", default=os.environ.get("LEGEND_NOTE"), help="Short note: how values were calculated (units, sources)")
    args = parser.parse_args()

    if args.input:
        df = load_data(args.input)
    else:
        df = pd.DataFrame(DEFAULT_DATA)

    build_map(
        df,
        args.geojson,
        args.output,
        args.geojson_key,
        legend_title=args.legend_title,
        legend_note=args.legend_note,
    )


if __name__ == "__main__":
    main()
