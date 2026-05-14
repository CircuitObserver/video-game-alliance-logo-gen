import streamlit as st
import requests
import io
import os
from PIL import Image

# API setup
API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
# This looks for a secret you'll set in the Streamlit Dashboard later
headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"}

st.set_page_config(page_title="ROK Logo Forge", page_icon="🛡️")

st.title("🛡️ ROK Alliance Logo Forge")
st.markdown("Create high-quality gaming emblems instantly.")

# User inputs
with st.sidebar:
    st.header("Customizer")
    style = st.selectbox("Theme", ["Medieval", "E-Sports", "Viking", "Royal"])
    color = st.text_input("Main Color", "Gold and Blue")

subject = st.text_input("Emblem Subject", placeholder="e.g., A fierce wolf, crossed swords, a dragon")

if st.button("Generate Logo", type="primary"):
    if subject:
        with st.spinner("Forging..."):
            # The prompt 'wrapper' ensures it looks like a game logo
            prompt = f"Professional gaming logo, shield emblem, {subject}, {style} style, {color} colors, flat vector art, white background, symmetrical."
            
            response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
            
            if response.status_code == 200:
                image = Image.open(io.BytesIO(response.content))
                st.image(image, use_container_width=True)
                
                # Prep for download
                buf = io.BytesIO()
                image.save(buf, format="PNG")
                st.download_button("Download Logo", buf.getvalue(), "alliance_logo.png", "image/png")
            else:
                st.error("Model busy. Please wait 10 seconds and try again.")
    else:
        st.warning("Please enter a subject!")