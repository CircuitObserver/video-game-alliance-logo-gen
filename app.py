import streamlit as st
import requests
import io
from PIL import Image, ImageDraw, ImageFont

# 1. Setup & Configuration
st.set_page_config(page_title="ROK Alliance Forge", page_icon="🛡️", layout="wide")

API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"

if "HF_TOKEN" not in st.secrets:
    st.error("🚨 Missing HF_TOKEN in Secrets!")
    st.stop()

headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"}

# 2. The Prompt Formula Engine
def generate_sleek_prompt(subject, style, bg_color):
    """
    Formula: [Symmetry/Format] [Core Subject] [Artistic Style] 
    [Background Specs] [Lighting/Finish] [Quality Anchors]
    """
    # Map styles to professional descriptors
    style_descriptors = {
        "Medieval Heraldry": "traditional coat of arms, ornate gold filigree, authentic noble crest",
        "E-Sports": "modern aggressive mascot, bold thick outlines, sharp geometric edges",
        "Royal": "elegant minimal crown aesthetic, luxury silk textures, regal gold accents",
        "Viking": "nordic rune style, weathered stone texture, primitive tribal carving"
    }
    
    descriptor = style_descriptors.get(style, "clean vector art")
    
    # The Formulaic Master Prompt
    return (
        f"A professional high-end gaming alliance emblem featuring {subject}. "
        f"Style: {descriptor}. "
        f"Composition: perfectly symmetrical, centered, isolated icon, no text. "
        f"Background: solid flat {bg_color}. "
        f"Lighting: studio rim lighting, 3D depth in a 2D vector style, high-contrast. "
        f"Quality: masterpiece, 8k, trending on ArtStation, clean lines, sharp focus."
    )

# 3. UI Layout
st.title("🛡️ ROK Alliance Logo Forge")
st.subheader("Create a professional gaming identity in seconds.")

with st.sidebar:
    st.header("🛠️ Design Controls")
    style_choice = st.selectbox("Aesthetic Style", ["Medieval Heraldry", "E-Sports", "Royal", "Viking"])
    bg_input = st.text_input("Background Color", "Dark Charcoal Grey")
    
    st.divider()
    st.header("Typography")
    alliance_name = st.text_input("Alliance Name", "IRON LEGION")
    text_color = st.color_picker("Text Color", "#D4AF37") # Default Gold
    font_size = st.slider("Text Size", 30, 120, 60)

# Main Inputs
subject_input = st.text_input("Emblem Icon", placeholder="e.g., A silver wolf with glowing eyes")

# 4. Forge Logic
if st.button("Generate Sleek Logo", type="primary"):
    if subject_input:
        with st.spinner("Executing Prompt Engine..."):
            
            final_prompt = generate_sleek_prompt(subject_input, style_choice, bg_input)
            
            response = requests.post(API_URL, headers=headers, json={"inputs": final_prompt})
            
            if response.status_code == 200:
                img = Image.open(io.BytesIO(response.content)).convert("RGBA")
                
                # Professional Text Overlay
                if alliance_name:
                    draw = ImageDraw.Draw(img)
                    try:
                        # Streamlit Cloud supports basic fonts; for custom, upload a .ttf to GitHub
                        font = ImageFont.load_default() 
                    except:
                        font = ImageFont.load_default()
                    
                    w, h = img.size
                    bbox = draw.textbbox((0, 0), alliance_name.upper(), font=font)
                    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
                    # Position slightly lower for a 'cinematic' look
                    draw.text(((w - tw) / 2, h * 0.88), alliance_name.upper(), fill=text_color, font=font)

                st.image(img, use_container_width=True)
                
                # Download
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                st.download_button("Download Professional PNG", buf.getvalue(), "alliance_logo.png")
            
            elif response.status_code == 503:
                st.info("The AI is preparing the forge. Please wait 20 seconds and click again.")
            else:
                st.error(f"Error {response.status_code}: {response.text}")
    else:
        st.warning("Please provide a subject for the emblem.")