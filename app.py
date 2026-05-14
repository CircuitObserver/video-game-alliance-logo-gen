import streamlit as st
import requests
import io
import os
from PIL import Image

st.set_page_config(page_title="ROK Alliance Forge", page_icon="🛡️")

# 1. NEW ENDPOINT URL (2026 Router)
API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"

# 2. Check for Token
if "HF_TOKEN" not in st.secrets:
    st.error("🚨 HF_TOKEN missing! Go to Streamlit Settings > Secrets and add your token.")
    st.stop()

headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"}

st.title("🛡️ ROK Alliance Logo Forge")

# Sidebar
with st.sidebar:
    st.header("Settings")
    style = st.selectbox("Theme", ["Medieval", "E-Sports", "Viking", "Royal"])
    color = st.text_input("Colors", "Gold and Crimson")

subject = st.text_input("Logo Subject", placeholder="e.g., A fierce wolf, crossed swords")

if st.button("Generate Logo", type="primary"):
    if subject:
        with st.spinner("Forging..."):
            prompt = f"Professional gaming logo, shield emblem, {subject}, {style} style, {color} colors, flat vector art, white background, symmetrical."
            
            # 3. Call the new Router API
            response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
            
            if response.status_code == 200:
                image = Image.open(io.BytesIO(response.content))
                st.image(image, use_container_width=True)
                
                buf = io.BytesIO()
                image.save(buf, format="PNG")
                st.download_button("Download PNG", buf.getvalue(), "alliance_logo.png", "image/png")
            
            elif response.status_code == 404:
                st.error("Error 404: The API address has changed. Use the 'router.huggingface.co' URL.")
            elif response.status_code == 503:
                st.info("The Forge is warming up. Please try again in 20 seconds.")
            else:
                st.error(f"Error {response.status_code}: {response.text}")
    else:
        st.warning("Enter a subject first!")