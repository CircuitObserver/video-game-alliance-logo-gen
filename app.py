import streamlit as st
import requests
import io
import os
from PIL import Image

# 1. Page Configuration
st.set_page_config(page_title="ROK Alliance Forge", page_icon="🛡️", layout="centered")

# 2. Secure Token Handling
# This looks for the HF_TOKEN in your Streamlit Cloud "Secrets" setting
try:
    HF_TOKEN = st.secrets["HF_TOKEN"]
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
except KeyError:
    st.error("🚨 **Configuration Error:** HF_TOKEN not found in Streamlit Secrets.")
    st.info("Go to your App Settings > Secrets and add: HF_TOKEN = 'your_token_here'")
    st.stop()

# 3. AI Model URL (FLUX.1-schnell is the fastest free-tier model)
API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"

# 4. User Interface
st.title("🛡️ ROK Alliance Logo Forge")
st.markdown("Generate custom emblems for your Rise of Kingdoms alliance.")

with st.sidebar:
    st.header("Design Settings")
    style = st.selectbox("Style Theme", [
        "Medieval Heraldry", 
        "E-Sports Mascot", 
        "Minimalist Vector", 
        "Royal Gold & Silk"
    ])
    color_scheme = st.text_input("Color Palette", "Gold, Crimson, and Black")
    st.divider()
    st.caption("Tip: FLUX excels at 'Flat Vector' styles for game icons.")

subject = st.text_input("Logo Subject", placeholder="e.g., A fierce dragon, crossed scimitars, a soaring eagle")

# 5. Generation Logic
if st.button("Generate Alliance Logo", type="primary"):
    if not subject:
        st.warning("Please enter a subject (e.g., 'A golden lion').")
    else:
        with st.spinner("⚒️ The blacksmith is forging your emblem..."):
            # This prompt wrapper ensures a professional logo result
            refined_prompt = (
                f"Professional gaming logo, shield emblem, {subject}, {style} style, "
                f"colors: {color_scheme}, flat vector art, symmetrical, high contrast, "
                f"white background, centered, 4k resolution."
            )
            
            try:
                response = requests.post(API_URL, headers=headers, json={"inputs": refined_prompt})
                
                if response.status_code == 200:
                    # Success
                    image_bytes = response.content
                    image = Image.open(io.BytesIO(image_bytes))
                    
                    st.image(image, caption=f"Emblem: {subject}", use_container_width=True)
                    
                    # Prepare Download
                    buf = io.BytesIO()
                    image.save(buf, format="PNG")
                    byte_im = buf.getvalue()
                    
                    st.download_button(
                        label="📥 Download Logo (PNG)",
                        data=byte_im,
                        file_name="alliance_logo.png",
                        mime="image/png",
                    )
                    
                elif response.status_code == 503:
                    # Model is loading
                    st.info("⏳ The AI model is currently 'warming up' on Hugging Face. Please wait about 30 seconds and click Generate again.")
                elif response.status_code == 401:
                    st.error("🔑 API Token invalid. Check your Hugging Face token permissions.")
                else:
                    st.error(f"❌ Error {response.status_code}: {response.text}")
                    
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

st.divider()
st.caption("Powered by FLUX.1 [schnell] via Hugging Face Inference API.")