import streamlit as st
from google import genai
from PIL import Image

st.set_page_config(page_title="Chetak MCQ Maker", page_icon="🐎")

st.title("🐎 Chetak MCQ Maker")
st.write("Notes ki image upload karke MCQ banaiye.")

# API Key
api_key = st.sidebar.text_input(
    "Gemini API Key",
    type="password"
)

# Image Upload
uploaded_file = st.file_uploader(
    "Notes Image Upload Karein",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None and api_key:

    image = Image.open(uploaded_file)

    st.image(image, caption="Uploaded Notes", use_container_width=True)

    number = st.slider(
        "Kitne MCQ Chahiye?",
        min_value=3,
        max_value=20,
        value=5
    )

    if st.button("✨ MCQ Taiyaar Karein"):

        try:
            client = genai.Client(api_key=api_key)

            prompt = f"""
Tum ek expert teacher ho.

Is image ko dhyan se padho aur uske basis par {number} MCQ banao.

Rules:
- Har question ke 4 options hone chahiye.
- Sirf ek answer correct ho.
- Har question ke niche Correct Answer likho.
- Language Hinglish rakho.
- Output clean markdown me do.
"""

            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[prompt, image]
            )

            st.success("✅ MCQ Taiyaar!")

            st.markdown(response.text)

        except Exception as e:
            st.error(f"Error: {e}")
