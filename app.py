import streamlit as st
import requests
import io
import os
from PIL import Image, ImageDraw, ImageFont

# 1. Page Configuration
st.set_page_config(page_title="ROK Alliance Forge", page_icon="🛡️")

# 2. API Setup (New 2026 Router URL)
API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"

if "HF_TOKEN" not in st.secrets:
    st.error("🚨 HF_TOKEN missing in Streamlit Secrets!")
    st.stop()

headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"}

# 3. Sidebar UI
with st.sidebar:
    st.header("🎨 Design Studio")
    style = st.selectbox("Theme", ["Medieval Heraldry", "E-Sports", "Royal", "Viking"])
    bg_color_name = st.text_input("Background Color", "Dark Slate Grey")
    text_color = st.color_picker("Alliance Name Color", "#FFFFFF")
    font_size = st.slider("Font Size", 20, 100, 50)

st.title("🛡️ ROK Alliance Logo Forge")

# 4. Main Inputs
col1, col2 = st.columns(2)
with col1:
    subject = st.text_input("Logo Subject", placeholder="e.g., A golden eagle")
with col2:
    alliance_name = st.text_input("Alliance Name", placeholder="e.g., IRON LEGION")

if st.button("Forge Logo", type="primary"):
    if subject:
        with st.spinner("Blacksmith is working..."):
            # Refined Prompt for better backgrounds
            prompt = (f"Professional gaming logo, shield emblem, {subject}, {style} style, "
                      f"on a solid {bg_color_name} background, flat vector art, symmetrical, "
                      f"high contrast, centered, masterpiece.")
            
            response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
            
            if response.status_code == 200:
                # Load the image from the AI
                base_image = Image.open(io.BytesIO(response.content)).convert("RGBA")
                
                # --- PILLOW TEXT SECTION ---
                if alliance_name:
                    draw = ImageDraw.Draw(base_image)
                    # Use a default font (Streamlit Cloud has some pre-installed)
                    try:
                        # Attempting to load a standard bold font
                        font = ImageFont.load_default() 
                    except:
                        font = ImageFont.load_default()

                    # Calculate text position (Centered at the bottom)
                    width, height = base_image.size
                    # textbbox gives us the size of the text
                    left, top, right, bottom = draw.textbbox((0, 0), alliance_name.upper(), font=font)
                    text_width = right - left
                    
                    # Position: Horizontal center, 10% up from bottom
                    position = ((width - text_width) / 2, height * 0.85)
                    
                    # Draw text on image
                    draw.text(position, alliance_name.upper(), fill=text_color, font=font)
                # ---------------------------

                st.image(base_image, caption=f"Emblem for {alliance_name}", use_container_width=True)
                
                # Prepare for Download
                buf = io.BytesIO()
                base_image.save(buf, format="PNG")
                st.download_button("📥 Download PNG", buf.getvalue(), "alliance_logo.png", "image/png")
            
            elif response.status_code == 503:
                st.info("Forge is warming up. Please try again in 20 seconds.")
            else:
                st.error(f"Error {response.status_code}: {response.text}")
    else:
        st.warning("Please enter a subject!")