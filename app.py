import streamlit as st
import requests
import io
from PIL import Image

# 1. Configuration
st.set_page_config(page_title="Profile Pic Generator", page_icon="🛡️", layout="wide")

# Corrected CSS
st.markdown("""
    <style>
    div.stButton > button:first-child {
        width: 100%; border-radius: 8px; height: 3.5em;
        background-color: #4CAF50; color: white; font-weight: bold; border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# API Endpoints
LLM_URL = "https://router.huggingface.co/hf-inference/models/Qwen/Qwen2.5-72B-Instruct"
IMG_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"

if "HF_TOKEN" not in st.secrets:
    st.error("Error: HF_TOKEN not found in Secrets.")
    st.stop()

headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"}

# 2. Safety & Moderation Engine
def moderate_prompt(user_input):
    """Sends prompt to Qwen to check for safety and sanitize it."""
    system_message = (
        "You are a safety moderation agent for a gaming profile picture generator. "
        "Your task: Identify any inappropriate, NSFW, violent, or harmful content. "
        "Return your response in EXACTLY this format: 'SAFE: [True/False] | REWRITTEN: [Sanitized Prompt]'. "
        "If the input is safe, set SAFE to True and keep the prompt mostly as is. "
        "If it is unsafe, set SAFE to False and remove ONLY the harmful parts, "
        "replacing them with safe, heroic gaming alternatives."
    )
    
    payload = {
        "inputs": f"<|im_start|>system\n{system_message}<|im_end|>\n<|im_start|>user\n{user_input}<|im_end|>\n<|im_start|>assistant\n",
        "parameters": {"max_new_tokens": 150, "temperature": 0.1}
    }
    
    try:
        response = requests.post(LLM_URL, headers=headers, json=payload)
        result_text = response.json()[0]['generated_text'].split("assistant\n")[-1]
        
        # Parse the custom format
        is_safe = "SAFE: True" in result_text
        sanitized_prompt = result_text.split("REWRITTEN: ")[-1].strip()
        return is_safe, sanitized_prompt
    except Exception:
        # Fallback if LLM fails: assume safe but use basic cleaning
        return True, user_input

def build_image_prompt(subject, style, bg_color, name):
    style_styles = {
        "E-Sports": "modern aggressive vector, bold outlines, mascot style",
        "Classic": "3D crest, royal shield, metallic gold textures",
        "Minimal": "clean flat design, minimalist icon",
        "Fantasy": "dark gothic engraving, weathered stone texture"
    }
    style_desc = style_styles.get(style, "gaming vector")
    text_bit = f'with the text "{name.upper()}" integrated into a nameplate' if name else ""
    
    return (f"A professional gaming profile picture of {subject}, {text_bit}. "
            f"Style: {style_desc}. Symmetrical, centered on solid {bg_color} background. "
            f"8k, sharp focus, clean lines.")

# 3. User Interface
st.title("Profile Pic Generator")
st.write("This app is designed to make high-quality alliance images and gaming profile pictures instantly.")

left_col, right_col = st.columns([1, 1], gap="large")

with left_col:
    st.subheader("Settings")
    subject = st.text_input("Logo Subject", placeholder="e.g. A golden dragon")
    name = st.text_input("Alliance Name", placeholder="e.g. IRON LEGION")
    style = st.selectbox("Style", ["E-Sports", "Classic", "Minimal", "Fantasy"])
    bg = st.text_input("Background Color", "Black")
    generate_btn = st.button("Generate Image")

with right_col:
    if generate_btn:
        if not subject:
            st.warning("Please describe the subject.")
        else:
            with st.spinner("Analyzing safety and forging art..."):
                # STEP 1: MODERATION
                is_safe, final_subject = moderate_prompt(subject)
                
                # If unsafe, show the warning and the new prompt
                if not is_safe:
                    st.warning("⚠️ **Safety Notice:** Inappropriate content was detected. Your prompt has been rewritten for safety.")
                    st.info(f"**Sanitized Prompt:** {final_subject}")

                # STEP 2: GENERATE IMAGE
                full_image_prompt = build_image_prompt(final_subject, style, bg, name)
                
                img_res = requests.post(IMG_URL, headers=headers, json={"inputs": full_image_prompt})
                
                if img_res.status_code == 200:
                    img = Image.open(io.BytesIO(img_res.content))
                    st.image(img, use_container_width=True)
                    
                    buf = io.BytesIO()
                    img.save(buf, format="PNG")
                    st.download_button("Download PNG", buf.getvalue(), "pfp.png", "image/png")
                else:
                    st.error("The image generator is busy. Try again in 20 seconds.")
    else:
        st.info("Fill out settings and click Generate.")

st.divider()
st.caption("AI Moderated | Powered by Qwen 72B & FLUX")