import streamlit as st
import requests
import json
import pandas as pd
import plotly.io as pio
import base64
import numpy as np

def decode_bdata(bdata: str, dtype: str):
    dtype_map = {
        'i2': np.int16,
        'i4': np.int32,
        'f8': np.float64
    }
    if dtype not in dtype_map:
        raise ValueError(f"Unsupported dtype: {dtype}")
    
    byte_data = base64.b64decode(bdata)
    return np.frombuffer(byte_data, dtype=dtype_map[dtype]).tolist()

def fix_plotly_template(plotly_json):
    """Fix common Plotly template issues"""
    # Navigate to template data if it exists
    if "layout" in plotly_json and "template" in plotly_json["layout"] and "data" in plotly_json["layout"]["template"]:
        template_data = plotly_json["layout"]["template"]["data"]
        
        # Fix scattermap -> scattermapbox
        if "scattermap" in template_data:
            template_data["scattermapbox"] = template_data.pop("scattermap")
        
        # Remove any other unsupported trace types that might cause issues
        supported_types = {
            'barpolar', 'bar', 'box', 'candlestick', 'carpet', 'choroplethmapbox', 
            'choropleth', 'cone', 'contourcarpet', 'contour', 'densitymapbox', 
            'funnelarea', 'funnel', 'heatmapgl', 'heatmap', 'histogram2dcontour', 
            'histogram2d', 'histogram', 'icicle', 'image', 'indicator', 'isosurface', 
            'mesh3d', 'ohlc', 'parcats', 'parcoords', 'pie', 'pointcloud', 
            'sankey', 'scatter3d', 'scattercarpet', 'scattergeo', 'scattergl', 
            'scattermapbox', 'scatterpolargl', 'scatterpolar', 'scatter', 
            'scattersmith', 'scatterternary', 'splom', 'streamtube', 'sunburst', 
            'surface', 'table', 'treemap', 'violin', 'volume', 'waterfall'
        }
        
        # Remove unsupported types
        keys_to_remove = [key for key in template_data.keys() if key not in supported_types]
        for key in keys_to_remove:
            template_data.pop(key, None)
    
    return plotly_json

def clean_plotly_json(plotly_json):
    # First fix template issues
    plotly_json = fix_plotly_template(plotly_json)
    
    # Then handle bdata decoding for all possible fields
    for trace in plotly_json.get("data", []):
        # Common fields that might have bdata encoding
        bdata_fields = [
            'x', 'y', 'z', 'text', 'hovertext', 'hovertemplate',
            'values', 'labels', 'parents', 'ids', 'customdata',
            'error_x', 'error_y', 'error_z', 'open', 'high', 'low', 'close'
        ]
        
        for field in bdata_fields:
            val = trace.get(field)
            if isinstance(val, dict) and 'bdata' in val and 'dtype' in val:
                try:
                    trace[field] = decode_bdata(val['bdata'], val['dtype'])
                except Exception as e:
                    # Set to appropriate default based on field type
                    if field in ['text', 'hovertext', 'hovertemplate']:
                        trace[field] = []  # Empty list for text fields
                    else:
                        trace[field] = []  # Empty list for numeric fields
        
        # Handle nested objects that might contain bdata (like marker, line, etc.)
        def clean_nested_dict(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, dict):
                        if 'bdata' in value and 'dtype' in value:
                            try:
                                obj[key] = decode_bdata(value['bdata'], value['dtype'])
                            except Exception:
                                obj[key] = []
                        else:
                            clean_nested_dict(value)
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, dict):
                                clean_nested_dict(item)
        
        # Clean nested structures
        for nested_field in ['marker', 'line', 'fill', 'error_x', 'error_y', 'error_z']:
            if nested_field in trace:
                clean_nested_dict(trace[nested_field])
    
    return plotly_json

# Streamlit config
st.set_page_config(page_title="Vanna Full Response Viewer", page_icon="https://vanna.ai/favicon.ico", layout="wide")

# API call function
def call_vanna_agent(agent_id: str, message: str, api_key: str, user_email: str):
    try:
        response = requests.post(
            "https://app.vanna.ai/api/v0/chat_sse",
            headers={
                "Content-Type": "application/json",
                "VANNA-API-KEY": api_key
            },
            data=json.dumps({
                "message": message,
                "user_email": user_email,
                "agent_id": agent_id,
                "acceptable_responses": [
                    "text", "image", "link", "buttons", "dataframe", "plotly", "sql"
                ]
            }),
            stream=True
        )

        responses = []

        for line in response.iter_lines():
            if line and line.decode("utf-8").startswith("data:"):
                data = json.loads(line.decode("utf-8")[5:].strip())
                responses.append(data)
        return responses
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return []

# Sidebar
with st.sidebar:
    st.header("🔐 Authentication")
    api_key = st.text_input("Vanna API Key", type="password", value="", placeholder="Enter your Vanna API key")
    user_email = st.text_input("User Email", value="", placeholder="Enter your email")
    agent_id = st.text_input("Agent ID", value="", placeholder="Enter your agent ID")

# Main UI
st.title("Vanna Full Response Viewer")
st.markdown("Explore all Vanna response types from a single query")

user_prompt = st.text_area("Your Prompt", placeholder="e.g., Show me usage stats by email")

if st.button("▶️ Run Query", type="primary"):
    if not api_key or not user_email or not agent_id or not user_prompt:
        st.warning("Please fill in all fields.")
    else:
        with st.spinner("Calling Vanna agent..."):
            responses = call_vanna_agent(agent_id, user_prompt, api_key, user_email)

        st.subheader("📦 Response Breakdown")

        for idx, data in enumerate(responses):
            dtype = data.get("type", "")
            st.markdown(f"### Response {idx+1} - `{dtype}`")
            if dtype == "text":
                st.info(data.get("text", ""))
            elif dtype == "image":
                image_url = data.get("image_url")
                if image_url and isinstance(image_url, str):
                    st.image(image_url, caption=data.get("caption", ""), use_column_width=True)
                else:
                    st.warning("⚠️ Image URL missing or invalid")
                    st.json(data)
            elif dtype == "link":
                st.markdown(f"[{data.get('title')}]({data.get('url')})")
                if data.get("description"):
                    st.caption(data.get("description"))
            elif dtype == "buttons":
                st.markdown(data.get("text", ""))
                for button in data.get("buttons", []):
                    st.button(button.get("label", "Unnamed Button"))
            elif dtype == "dataframe":
                df = pd.DataFrame(data["json_table"]["data"])
                st.dataframe(df, use_container_width=True)
            elif dtype == "plotly":
                try:
                    cleaned = clean_plotly_json(data["json_plotly"])
                    fig = pio.from_json(json.dumps(cleaned))
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Show raw plotly JSON for reference
                    with st.expander("View Plotly JSON", expanded=False):
                        st.json(data["json_plotly"])
                except Exception as e:
                    st.error("⚠️ Plotly render failed")
                    st.exception(e)
                    st.json(data["json_plotly"])
            elif dtype == "sql":
                st.code(data.get("query", ""), language="sql")
            elif dtype == "error":
                st.error(data.get("error", "Unknown error"))
            elif dtype == "end":
                st.success("✅ End of response stream")
            else:
                st.warning(f"Unknown response type: {dtype}")
                st.json(data)

# Footer
st.markdown("---")
st.caption("Built with Streamlit • Powered by Vanna AI")