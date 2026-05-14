import streamlit as st
import requests
import io
from PIL import Image

# 1. Page Configuration
st.set_page_config(page_title="Profile Pic Generator", page_icon="🛡️", layout="wide")

# Custom UI Styling
st.markdown("""
    <style>
    div.stButton > button:first-child {
        width: 100%; border-radius: 8px; height: 3.5em;
        background-color: #2E7D32; color: white; font-weight: bold; border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# API Endpoints
LLM_URL = "https://router.huggingface.co/hf-inference/models/Qwen/Qwen2.5-72B-Instruct"
IMG_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"

if "HF_TOKEN" not in st.secrets:
    st.error("Missing HF_TOKEN in Secrets.")
    st.stop()

headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"}

# 2. Hard-Coded Keyword Refusal (Python Layer)
def check_hard_refusal(text):
    """Zero-tolerance local check for underage/child-related keywords."""
    forbidden = [
        "child", "children", "kid", "kids", "underage", "minor", "minors", 
        "toddler", "baby", "babies", "infant", "schoolgirl", "schoolboy", 
        "youth", "teen", "teenager", "juvenile"
    ]
    words = text.lower().split()
    return any(word in words for word in forbidden)

# 3. Moderation Layer
def moderate_prompt(user_input):
    # Immediate Local Refusal
    if check_hard_refusal(user_input):
        return "HARD_REFUSE", ""

    # Instruction for Qwen (Fixed Balanced Strictness)
    system_message = """
    You are a strict Safety Moderator. 
    
    CRITICAL RULE:
    ANY mention of children, minors, underage individuals, or anything insinuating such topics MUST be rejected instantly. 
    It does not matter if the context seems 'safe'—if it relates to children, you MUST set SAFE: False and return an empty REWRITTEN field.

    GENERAL POLICY:
    - Balanced moderation: allow epic battle imagery but remove graphic gore.
    - If input contains NSFW content or real-world hate speech, set SAFE: False.
    - REWRITE flagged content into professional, heroic gaming themes.
    
    OUTPUT FORMAT:
    SAFE: [True/False]
    REWRITTEN: [Sanitized Prompt]
    """
    
    payload = {
        "inputs": f"<|im_start|>system\n{system_message}<|im_end|>\n<|im_start|>user\n{user_input}<|im_end|>\n<|im_start|>assistant\n",
        "parameters": {"max_new_tokens": 200, "temperature": 0.1}
    }
    
    try:
        response = requests.post(LLM_URL, headers=headers, json=payload, timeout=10)
        result_text = response.json()[0]['generated_text'].split("assistant\n")[-1]
        
        # Check for child-related refusals in the AI output
        if "SAFE: False" in result_text and (not result_text.split("REWRITTEN:")[-1].strip()):
            return "HARD_REFUSE", ""
            
        is_safe = "SAFE: True" in result_text
        sanitized = result_text.split("REWRITTEN:")[-1].strip() if "REWRITTEN:" in result_text else user_input
        return is_safe, sanitized
    except:
        return True, user_input

# 4. User Interface
st.title("Profile Pic Generator")
st.write("Professional alliance and clan images forged instantly.")

st.divider()

with st.sidebar:
    st.header("⚙️ Settings")
    style_choice = st.selectbox("Style Aesthetic", ["E-Sports", "Classic", "Minimal", "Fantasy"])
    bg_color = st.text_input("Background Color", "Dark Charcoal")
    
    st.divider()
    # Simple Disclaimer as requested
    st.caption("⚠️ AI is being used for the moderation layer.")

# Main Inputs
col1, col2 = st.columns(2)
with col1:
    subject_input = st.text_input("Logo Subject", placeholder="e.g. A cybernetic knight")
with col2:
    alliance_name = st.text_input("Alliance Name", placeholder="e.g. VANGUARD")

if st.button("Forge Image", type="primary"):
    if not subject_input:
        st.warning("Please enter a subject.")
    else:
        with st.spinner("Processing safety and design..."):
            # MODERATION
            is_safe, final_subject = moderate_prompt(subject_input)
            
            if is_safe == "HARD_REFUSE":
                st.error("inappropriate will not send this request.")
                st.stop()
            
            if not is_safe:
                st.warning("🛡️ Your prompt was refined for a better gaming aesthetic.")

            # IMAGE GENERATION
            full_img_prompt = (f"Professional gaming logo, {final_subject}, symmetrical, "
                              f"{style_choice} style, {bg_color} background")
            if alliance_name:
                full_img_prompt += f", integrated text '{alliance_name.upper()}'"

            img_res = requests.post(IMG_URL, headers=headers, json={"inputs": full_img_prompt})
            
            if img_res.status_code == 200:
                img = Image.open(io.BytesIO(img_res.content))
                st.image(img, use_container_width=True)
                
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                st.download_button("Download PNG", buf.getvalue(), "pfp.png", "image/png")
            else:
                st.error("Service busy, please try again in a few moments.")

st.divider()
st.caption("Multi-layer moderation active. Professional Gaming Use Only.")