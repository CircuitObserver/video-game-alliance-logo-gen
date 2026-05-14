import streamlit as st
import requests
import io
from PIL import Image

# 1. Page Configuration
st.set_page_config(page_title="Profile Pic Generator", page_icon="🛡️", layout="wide")

# Dark mode styling for a clean gamer look
st.markdown("""
    <style>
    stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3.5em;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    </style>
    """, unsafe_content_safe=True)

# 2. API Connection
API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"

if "HF_TOKEN" not in st.secrets:
    st.error("Error: HF_TOKEN not found in Streamlit Secrets.")
    st.stop()

headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"}

def build_prompt(subject, style, bg_color, name):
    """
    Structured formula to ensure the AI creates high-end gaming emblems.
    """
    style_styles = {
        "E-Sports": "modern aggressive vector, thick bold outlines, mascot style, sharp geometric shading",
        "Classic": "3D embossed crest, royal shield, metallic and gold textures, heraldic filigree",
        "Minimal": "clean flat vector design, modern minimalist aesthetic, symmetrical icon",
        "Fantasy": "dark gothic engraving, weathered stone texture, ancient cinematic atmosphere"
    }
    
    style_desc = style_styles.get(style, "professional gaming vector")
    
    # Direct instruction for the AI to include the text within the artwork
    text_instruction = f'including the text "{name.upper()}" clearly displayed on a professional banner or nameplate at the base of the emblem' if name else "without any text"

    return (
        f"A professional high-end gaming profile picture, a centered symmetrical emblem of {subject}, {text_instruction}. "
        f"Style: {style_desc}. "
        f"Composition: Square 1:1 ratio, centered on a solid {bg_color} background. "
        f"Typography: Integrated into the design, bold readable font, matching the texture of the emblem. "
        f"Quality: Masterpiece, 8k, sharp focus, clean lines, no spelling errors."
    )

# 3. User Interface
st.title("Profile Pic Generator")
st.write("Generate professional alliance, guild, or clan images for your favorite games.")

st.divider()

# Layout
left_col, right_col = st.columns([1, 1], gap="large")

with left_col:
    st.subheader("Settings")
    subject = st.text_input("Logo Subject", placeholder="e.g. A golden dragon, a blue wolf, crossed swords")
    name = st.text_input("Alliance Name", placeholder="e.g. IRON LEGION")
    
    style = st.selectbox("Style", ["E-Sports", "Classic", "Minimal", "Fantasy"])
    bg = st.text_input("Background Color", "Black")
    
    generate_btn = st.button("Generate Image")

with right_col:
    if generate_btn:
        if not subject:
            st.warning("Please describe what should be in the logo.")
        else:
            with st.spinner("Generating your image..."):
                final_prompt = build_prompt(subject, style, bg, name)
                
                try:
                    response = requests.post(API_URL, headers=headers, json={"inputs": final_prompt})
                    
                    if response.status_code == 200:
                        img = Image.open(io.BytesIO(response.content))
                        st.image(img, use_container_width=True)
                        
                        # Download button
                        buf = io.BytesIO()
                        img.save(buf, format="PNG")
                        st.download_button(
                            label="Download PNG",
                            data=buf.getvalue(),
                            file_name="alliance_pfp.png",
                            mime="image/png"
                        )
                    elif response.status_code == 503:
                        st.info("AI is loading. Please wait 10-20 seconds and click Generate again.")
                    else:
                        st.error(f"Error: {response.status_code}")
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        st.info("Fill out the settings and click Generate to see your logo here.")

st.divider()
st.caption("Free AI Image Generator | Powered by FLUX")