import streamlit as st
import requests
import io
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(page_title="ROK Alliance Forge", page_icon="🛡️", layout="wide")

API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"

if "HF_TOKEN" not in st.secrets:
    st.error("🚨 Missing HF_TOKEN in Secrets!")
    st.stop()

headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"}

def generate_integrated_prompt(subject, style, bg_color):
    style_descriptors = {
        "Medieval Heraldry": "metallic crest, embossed gold filigree, royal shield emblem",
        "E-Sports": "aggressive gaming mascot, thick bold outlines, sharp vector edges",
        "Royal": "minimalist luxury crown, silk and gold textures, elegant symmetrical icon",
        "Viking": "carved stone rune, weathered wood texture, ancient tribal emblem"
    }
    descriptor = style_descriptors.get(style, "clean vector art")
    
    # Formulaic Prompt: We ask for a "Badge" or "Emblem" specifically
    return (
        f"A professional sleek gaming badge featuring {subject}. "
        f"Style: {descriptor}. "
        f"Composition: Centered emblem, symmetrical, high-quality vector, "
        f"on a solid {bg_color} background. "
        f"Note: The bottom of the emblem should have a clean horizontal area for a nameplate. "
        f"Masterpiece, sharp focus, 8k, trending on ArtStation."
    )

st.title("🛡️ ROK Alliance Logo Forge")

with st.sidebar:
    st.header("🛠️ Design Controls")
    style_choice = st.selectbox("Aesthetic Style", ["Medieval Heraldry", "E-Sports", "Royal", "Viking"])
    bg_input = st.text_input("Background Color", "Dark Charcoal")
    
    st.divider()
    st.header("Typography & Integration")
    alliance_name = st.text_input("Alliance Name", "IRON LEGION")
    text_color = st.color_picker("Text Color", "#D4AF37")
    banner_opacity = st.slider("Banner Opacity", 0, 255, 180) # Controls the nameplate background

subject_input = st.text_input("Emblem Icon", placeholder="e.g., A crimson phoenix")

if st.button("Generate Integrated Logo", type="primary"):
    if subject_input:
        with st.spinner("Forging..."):
            final_prompt = generate_integrated_prompt(subject_input, style_choice, bg_input)
            response = requests.post(API_URL, headers=headers, json={"inputs": final_prompt})
            
            if response.status_code == 200:
                img = Image.open(io.BytesIO(response.content)).convert("RGBA")
                draw = ImageDraw.Draw(img, "RGBA")
                w, h = img.size
                
                if alliance_name:
                    # 1. Setup Font (Defaulting to large/bold)
                    font = ImageFont.load_default() 
                    
                    # 2. Measure Text
                    name_upper = alliance_name.upper()
                    bbox = draw.textbbox((0, 0), name_upper, font=font)
                    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
                    
                    # 3. Create "Integrated" Nameplate (Banner)
                    # We place it at roughly 75% height of the image
                    rect_h = th + 40
                    rect_y = (h * 0.75)
                    
                    # Draw semi-transparent background bar for the text
                    # Using a darker version of the BG or black
                    draw.rectangle(
                        [((w - tw) / 2) - 20, rect_y, ((w + tw) / 2) + 20, rect_y + rect_h],
                        fill=(0, 0, 0, banner_opacity)
                    )
                    
                    # 4. Draw Text over the Banner
                    draw.text(((w - tw) / 2, rect_y + 15), name_upper, fill=text_color, font=font)

                st.image(img, use_container_width=True)
                
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                st.download_button("Download PNG", buf.getvalue(), "alliance_logo.png")
            else:
                st.error(f"Error {response.status_code}")
    else:
        st.warning("Please enter a subject.")