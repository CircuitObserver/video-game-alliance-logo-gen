import streamlit as st
import requests
import io
from PIL import Image

st.set_page_config(page_title="ROK AI Forge", page_icon="🛡️", layout="wide")

API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"

if "HF_TOKEN" not in st.secrets:
    st.error("🚨 Missing HF_TOKEN in Secrets!")
    st.stop()

headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"}

def generate_unified_prompt(subject, style, bg_color, alliance_name):
    """
    This formula merges the art and text into a single instruction set for the AI.
    """
    style_descriptors = {
        "Medieval Heraldry": "metallic 3D crest, embossed gold filigree, authentic royal shield",
        "E-Sports": "modern aggressive gaming mascot, thick bold vector outlines, neon accents",
        "Royal": "minimalist luxury crown aesthetic, silk and gold textures, elegant symmetry",
        "Viking": "carved stone rune, weathered wood texture, ancient tribal aesthetic"
    }
    
    descriptor = style_descriptors.get(style, "sleek vector art")
    
    # We use quotes around the text to signal to FLUX that it needs to render these specific characters.
    text_instruction = f'with the text "{alliance_name.upper()}" integrated into the bottom of the design' if alliance_name else ""

    return (
        f"A professional high-end gaming alliance emblem featuring {subject}, {text_instruction}. "
        f"Style: {descriptor}. "
        f"Typography: The text is part of the emblem, bold, cinematic, and perfectly integrated into the base of the shield. "
        f"Composition: Symmetrical, centered, on a solid {bg_color} background. "
        f"Quality: Masterpiece, 8k, sharp lines, studio lighting, no spelling errors, highly detailed."
    )

st.title("🛡️ ROK Alliance AI Forge")
st.caption("Art and Typography forged simultaneously by the AI.")

with st.sidebar:
    st.header("Design Controls")
    style_choice = st.selectbox("Style", ["Medieval Heraldry", "E-Sports", "Royal", "Viking"])
    bg_input = st.text_input("Background Color", "Dark Slate Grey")
    st.divider()
    alliance_name = st.text_input("Alliance Name", "IRON LEGION")

subject_input = st.text_input("Emblem Subject", placeholder="e.g., A golden lion head")

if st.button("Forge Unified Logo", type="primary"):
    if subject_input:
        with st.spinner("AI is forging the emblem and text..."):
            
            final_prompt = generate_unified_prompt(subject_input, style_choice, bg_input, alliance_name)
            
            # Send the request to FLUX
            response = requests.post(API_URL, headers=headers, json={"inputs": final_prompt})
            
            if response.status_code == 200:
                # The AI returns the final image with text already on it
                img = Image.open(io.BytesIO(response.content))
                
                st.image(img, use_container_width=True)
                
                # Download
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                st.download_button("Download AI-Forged PNG", buf.getvalue(), "alliance_logo.png")
            
            elif response.status_code == 503:
                st.info("The AI Forge is warming up. Please try again in 20 seconds.")
            else:
                st.error(f"Error {response.status_code}: {response.text}")
    else:
        st.warning("Please provide a subject.")