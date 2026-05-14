import streamlit as st
import requests
import io
from PIL import Image

# 1. Page Configuration
st.set_page_config(page_title="Profile Pic Generator", page_icon="🛡️", layout="wide")

# Custom CSS for a professional look
st.markdown("""
    <style>
    div.stButton > button:first-child {
        width: 100%; border-radius: 8px; height: 3.5em;
        background-color: #4CAF50; color: white; font-weight: bold; border: none;
    }
    .stAlert {
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# API Configuration
LLM_URL = "https://router.huggingface.co/hf-inference/models/Qwen/Qwen2.5-72B-Instruct"
IMG_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"

if "HF_TOKEN" not in st.secrets:
    st.error("Critical Error: HF_TOKEN not found in Secrets.")
    st.stop()

headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"}

# 2. Safety & Moderation Engine (Zero-Tolerance)
def moderate_prompt(user_input):
    """Enhanced zero-tolerance moderation using XML structure and specific criteria."""
    system_message = """
    You are a strict Content Safety Officer for a family-friendly gaming site.
    
    CRITERIA FOR 'SAFE: False':
    - Any mention of blood, gore, wounds, or bodily fluids (even for fantasy monsters).
    - Realistic modern weapons (guns, assault rifles, realistic knives).
    - Sexual, suggestive, or NSFW language.
    - Toxicity: insults (loser, noob), hate speech, or harassment.
    - Illegal acts, drugs, or smoking references.

    INSTRUCTIONS:
    1. Analyze the user prompt.
    2. If ANY criteria are met, set SAFE: False.
    3. REWRITE the prompt into a heroic, professional gaming version.
       - Replace blood with 'glowing energy' or 'magical aura'.
       - Replace guns with 'sci-fi blasters' or 'energy staves'.
       - Replace toxicity with 'valiant' or 'champion'.
    
    OUTPUT FORMAT:
    <moderation>
    SAFE: [True/False]
    REWRITTEN: [Your sanitized version]
    </moderation>
    """
    
    payload = {
        "inputs": f"<|im_start|>system\n{system_message}<|im_end|>\n<|im_start|>user\n{user_input}<|im_end|>\n<|im_start|>assistant\n<moderation>\n",
        "parameters": {"max_new_tokens": 250, "temperature": 0.1}
    }
    
    try:
        response = requests.post(LLM_URL, headers=headers, json=payload, timeout=10)
        # Force extraction from the <moderation> tag
        result_text = response.json()[0]['generated_text'].split("<moderation>\n")[-1]
        
        is_safe = "SAFE: True" in result_text
        # Clean up the REWRITTEN part
        sanitized = result_text.split("REWRITTEN: ")[-1].replace("</moderation>", "").strip()
        
        return is_safe, sanitized
    except Exception as e:
        # Fallback for safety
        return True, user_input

def build_image_prompt(subject, style, bg_color, name):
    style_styles = {
        "E-Sports": "modern aggressive vector, thick bold outlines, mascot style, sharp geometric shading",
        "Classic": "3D embossed crest, royal shield, metallic gold textures, heraldic filigree",
        "Minimal": "clean flat vector design, modern minimalist aesthetic, symmetrical icon",
        "Fantasy": "dark gothic engraving, weathered stone texture, ancient cinematic atmosphere"
    }
    style_desc = style_styles.get(style, "gaming vector")
    
    # Prompting FLUX to render the text naturally
    text_bit = f'including the text "{name.upper()}" clearly displayed on a professional nameplate at the base of the emblem' if name else "without any text"

    return (
        f"A professional high-end gaming profile picture, a centered symmetrical emblem of {subject}, {text_bit}. "
        f"Style: {style_desc}. Composition: Square 1:1, centered on a solid {bg_color} background. "
        f"Quality: Masterpiece, 8k, sharp focus, clean lines, professional typography."
    )

# 3. User Interface
st.title("Profile Pic Generator")
st.write("This app is designed to make high-quality alliance images, clan logos, and gaming profile pictures instantly.")

st.divider()

left_col, right_col = st.columns([1, 1], gap="large")

with left_col:
    st.subheader("Settings")
    subject_input = st.text_input("Logo Subject", placeholder="e.g. A golden lion head")
    alliance_name = st.text_input("Alliance Name", placeholder="e.g. TITAN SQUAD")
    
    style_choice = st.selectbox("Style Aesthetic", ["E-Sports", "Classic", "Minimal", "Fantasy"])
    bg_color = st.text_input("Background Color", "Dark Grey")
    
    generate_btn = st.button("Generate Image")

with right_col:
    if generate_btn:
        if not subject_input:
            st.warning("Please enter a subject for your logo.")
        else:
            with st.spinner("Moderating prompt and forging art..."):
                # STEP 1: MODERATION LAYER
                is_safe, sanitized_subject = moderate_prompt(subject_input)
                
                # If unsafe, show warning and sanitized result
                if not is_safe:
                    st.warning("⚠️ **Safety Notice:** Inappropriate content was detected. Your prompt has been rewritten for safety.")
                    st.info(f"**Sanitized to:** {sanitized_subject}")

                # STEP 2: IMAGE GENERATION LAYER
                final_img_prompt = build_image_prompt(sanitized_subject, style_choice, bg_color, alliance_name)
                
                try:
                    img_res = requests.post(IMG_URL, headers=headers, json={"inputs": final_img_prompt}, timeout=30)
                    
                    if img_res.status_code == 200:
                        img = Image.open(io.BytesIO(img_res.content))
                        st.image(img, use_container_width=True)
                        
                        # Download Section
                        buf = io.BytesIO()
                        img.save(buf, format="PNG")
                        st.download_button(
                            label="Download PNG",
                            data=buf.getvalue(),
                            file_name=f"{alliance_name if alliance_name else 'logo'}.png",
                            mime="image/png"
                        )
                    elif img_res.status_code == 503:
                        st.info("The AI model is currently loading. Please wait 15 seconds and try again.")
                    else:
                        st.error(f"Image API Error: {img_res.status_code}")
                except Exception as e:
                    st.error(f"Generation failed: {e}")
    else:
        st.info("Fill out the settings on the left to generate your custom profile picture.")

st.divider()
st.caption("Gaming Profile Pic Generator | Managed Safety via Qwen 2.5-72B | Image Engine: FLUX.1 [schnell]")