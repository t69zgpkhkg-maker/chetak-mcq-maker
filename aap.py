import streamlit as st
from openai import OpenAI
from PIL import Image
import base64
import io
import json

st.set_page_config(
    page_title="AI MCQ Quiz Generator",
    page_icon="📚",
    layout="wide"
)

st.title("📚 AI MCQ Quiz Generator")
st.write("Upload Notes Image and Generate MCQs")

api_key = st.sidebar.text_input(
    "OpenRouter API Key",
    type="password"
)

uploaded_file = st.file_uploader(
    "Upload Notes Image",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file and api_key:

    image = Image.open(uploaded_file)

    st.image(image, use_container_width=True)

    mcq_count = st.slider(
        "Number of MCQs",
        5,
        20,
        10
    )

    if st.button("Generate MCQs"):

        with st.spinner("Generating..."):

            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            img_base64 = base64.b64encode(
                buffer.getvalue()
            ).decode()

            client = OpenAI(
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1"
            )

            prompt = f"""
Read this notes image carefully.

Generate exactly {mcq_count} multiple choice questions.

Return ONLY valid JSON.

Format:

[
 {{
  "question":"....",
  "options":[
   "A",
   "B",
   "C",
   "D"
  ],
  "answer":"A"
 }}
]
"""

            response = client.chat.completions.create(
                model="openrouter/auto",
                messages=[
                    {
                        "role":"user",
                        "content":[
                            {
                                "type":"text",
                                "text":prompt
                            },
                            {
                                "type":"image_url",
                                "image_url":{
                                    "url":f"data:image/png;base64,{img_base64}"
                                }
                            }
                        ]
                    }
                ]
            )

            output = response.choices[0].message.content

            st.subheader("Generated MCQs")

            st.code(output)

            try:
                data = json.loads(output)

                st.success("MCQs Generated Successfully")

                st.session_state.mcqs = data

            except Exception:

                st.warning("Model returned non-JSON output.")
                st.write(output)
# ---------------- QUIZ ENGINE ---------------- #

if "mcqs" in st.session_state:

    st.divider()
    st.header("📝 Quiz")

    if "current" not in st.session_state:
        st.session_state.current = 0
        st.session_state.score = 0

    mcqs = st.session_state.mcqs

    if st.session_state.current < len(mcqs):

        q = mcqs[st.session_state.current]

        st.subheader(
            f"Question {st.session_state.current+1}/{len(mcqs)}"
        )

        st.write(q["question"])

        option = st.radio(
            "Choose Answer",
            q["options"],
            key=f"q{st.session_state.current}"
        )

        if st.button("Next"):

            if option == q["answer"]:
                st.session_state.score += 1

            st.session_state.current += 1

            st.rerun()

    else:

        st.success("🎉 Quiz Completed!")

        st.metric(
            "Your Score",
            f"{st.session_state.score}/{len(mcqs)}"
        )

        percent = (
            st.session_state.score /
            len(mcqs)
        ) * 100

        st.progress(int(percent))

        st.write(f"Percentage : {percent:.1f}%")

        if st.button("Restart Quiz"):

            del st.session_state.current
            del st.session_state.score
            del st.session_state.mcqs

            st.rerun()
