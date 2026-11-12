import streamlit as st
import re, os
import numpy as np
import cv2
from PIL import Image
from google import genai
from dotenv import load_dotenv

load_dotenv()
st.set_page_config(page_title="Sketch to Website", layout="wide")
st.title("✏️ Sketch to Website")
st.write("Sketch upload karo, website ban jayegi!")

style = st.sidebar.selectbox("Style Chuno", ["Modern Blue", "Dark Mode", "Minimal White"])
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

def preprocess(original):
    img_np = np.array(original.convert("RGB"))
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    return gray
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    return Image.fromarray(cv2.cvtColor(enhanced, cv2.COLOR_GRAY2RGB))

def clean(text):
    text = re.sub(r'```html', '', text, flags=re.IGNORECASE)
    return text.replace("```","").strip()

uploaded = st.file_uploader("Apna Sketch Upload Karo", type=["png","jpg","jpeg"])

if uploaded:
    original = Image.open(uploaded)
    processed = preprocess(original)
    c1, c2 = st.columns(2)
    c1.image(original, caption="1. Tumhara Sketch")
    c2.image(processed, caption="2. AI ne Saaf Kiya")
    if st.button("✨ Website Banao", type="primary"):
        with st.spinner("Bana raha hu..."):
            prompt = f"Convert this hand-drawn wireframe to single-file HTML with Tailwind CSS via CDN. Style: {style}. Keep same layout. Only return HTML code."
            res = client.models.generate_content(model="gemini-2.5-flash", contents=[processed, prompt])
            code = clean(res.text)
            st.session_state['code'] = code

if 'code' in st.session_state:
    st.components.v1.html(st.session_state['code'], height=700, scrolling=True)
    st.download_button("⬇️ Download Website", st.session_state['code'], file_name="my-website.html", mime="text/html")
