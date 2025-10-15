import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_echarts import st_echarts
import json

# Optional imports for new components
try:
    from streamlit_ace import st_ace
    ACE_AVAILABLE = True
except Exception:
    ACE_AVAILABLE = False

try:
    from streamlit_lightweight_charts import st_lightweight_charts
    LIGHT_CHART_AVAILABLE = True
except Exception:
    LIGHT_CHART_AVAILABLE = False


def render_component(tag_type: str, params: dict):
    """
    Render components safely based on <tag> type and key-value params.
    Returns True if successful.
    """
    try:
        tag = tag_type.lower()

        # ---------- ECHARTS ----------
        if tag == "chart":
            data_str = params.get("data", "[]")
            try:
                data = json.loads(data_str)
            except json.JSONDecodeError:
                st.warning("Invalid chart data JSON. Using default data.")
                data = [{"value": 10, "name": "Sample"}]

            # detect numeric/x keys automatically
            if data and isinstance(data[0], dict):
                keys = list(data[0].keys())
                # try to find value-like and label-like keys
                if "value" not in keys:
                    value_key = next((k for k in keys if k.lower() in ["population", "y", "count", "score", "amount"]), keys[-1])
                else:
                    value_key = "value"
                if "name" not in keys:
                    name_key = next((k for k in keys if k.lower() in ["year", "x", "label"]), keys[0])
                else:
                    name_key = "name"
                x_vals = [str(d.get(name_key, "")) for d in data]
                y_vals = [float(d.get(value_key, 0)) for d in data]
            else:
                st.warning("Unexpected chart data format. Expected a list of dicts.")
                x_vals = list(range(len(data)))
                y_vals = data

            chart_type = params.get("type", "bar")

            options = {
                "tooltip": {"trigger": "axis"},
                "xAxis": {"type": "category", "data": x_vals},
                "yAxis": {"type": "value"},
                "series": [
                    {"type": chart_type, "data": y_vals, "smooth": True if chart_type == "line" else False}
                ],
            }

            st_echarts(options=options, height="400px")
            return True

        # ---------- MAP ----------
        elif tag == "map":
            lat = float(params.get("lat", 40.7128))
            lon = float(params.get("lon", -74.0060))
            m = folium.Map(location=[lat, lon], zoom_start=12)
            folium.Marker([lat, lon], popup="Location").add_to(m)
            st_folium(m, height=400, width=700)
            return True

        # ---------- CODE / EMBEDCODE ----------
        elif tag in ("code", "embedcode"):
            language = params.get("language", "python")
            default_content = params.get("content", 'print("Hello")')
            st.markdown(f"**Code Editor ({language})**")
            if tag == "embedcode" and ACE_AVAILABLE:
                code_val = st_ace(value=default_content, language=language, theme="monokai", height=250)
                st.code(code_val, language=language)
            else:
                st.text_area("Edit code:", value=default_content, height=200)
                st.code(default_content, language=language)
            return True

        # ---------- LIGHTCHART ----------
        elif tag in ("lightchart", "lightweightchart"):
            series_str = params.get("series", "[]")
            labels_str = params.get("labels", "[]")
            try:
                series = json.loads(series_str)
            except Exception:
                series = [10, 20, 15, 30]
            try:
                labels = json.loads(labels_str)
            except Exception:
                labels = list(range(len(series)))

            if LIGHT_CHART_AVAILABLE:
                config = {
                    "series": [{
                        "name": params.get("name", "Series 1"),
                        "data": [{"time": str(labels[i]), "value": series[i]} for i in range(len(series))]
                    }]
                }
                st_lightweight_charts(config)
            else:
                import pandas as pd
                st.line_chart(pd.DataFrame({"value": series}, index=labels))
            return True

        else:
            st.warning(f"Unknown component type: {tag}")
            return False

    except Exception as e:
        st.error(f"Render error for {tag_type}: {str(e)}")
        return False
