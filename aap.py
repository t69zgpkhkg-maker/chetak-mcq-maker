import streamlit as st
from google import genai
from PIL import Image

st.set_page_config(
    page_title="Chetak MCQ Maker",
    page_icon="🐎"
)

st.title("🐎 Chetak MCQ Maker")
st.write("Notes ki photo upload karo aur MCQ banao")

api_key = st.sidebar.text_input(
    "Gemini API Key",
    type="password"
)

uploaded_file = st.file_uploader(
    "Notes ki photo upload karo",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file and api_key:

    image = Image.open(uploaded_file)

    st.image(
        image,
        caption="Uploaded Notes",
        use_container_width=True
    )

    number = st.slider(
        "Kitne MCQ chahiye?",
        3,
        20,
        5
    )

    if st.button("✨ MCQ Taiyaar Karein"):

        client = genai.Client(api_key=api_key)

        prompt = f"""
        Is notes image se {number} MCQ banao.
        Har question ke 4 options do.
        Correct answer mark karo.
        Language Hinglish rakho.
        """

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[image, prompt]
        )

        st.success("MCQ Taiyaar!")
        st.write(response.text)
