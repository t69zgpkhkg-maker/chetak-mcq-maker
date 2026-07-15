# -*- coding: utf-8 -*-
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

Rules:
- Questions must be written in Hindi.
- Each question must have exactly 4 options.
- Only one option is correct.
- The answer must be only A, B, C or D.
- Return ONLY valid JSON.
- Do NOT write markdown.
- Do NOT use ```json.
- Do NOT explain anything.

Return exactly in this format:

[
  {{
    "question":"प्रश्न",
    "options":[
      "विकल्प A",
      "विकल्प B",
      "विकल्प C",
      "विकल्प D"
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

            

            

            try:
                data = json.loads(output)

                st.success("MCQs Generated Successfully")

                st.session_state.mcqs = data

            except Exception:

                st.warning("Model returned non-JSON output.")
                st.write(output)
# ---------------- QUIZ ENGINE ---------------- #

# ---------------- QUIZ ENGINE ---------------- #

if "mcqs" in st.session_state:

    st.divider()
    st.header("📝 Quiz")

    if "current" not in st.session_state:
        st.session_state.current = 0

    if "score" not in st.session_state:
        st.session_state.score = 0

    mcqs = st.session_state.mcqs

    if st.session_state.current < len(mcqs):

        q = mcqs[st.session_state.current]

        # Progress Bar
        progress = st.session_state.current / len(mcqs)
        st.progress(progress)

        st.subheader(
            f"Question {st.session_state.current + 1}/{len(mcqs)}"
        )

        st.write(q["question"])

        option = st.radio(
            "उत्तर चुनें",
            q["options"],
            key=f"q{st.session_state.current}"
        )

        if st.button("Next ➡️"):

            correct_option = q["options"][ord(q["answer"]) - 65]

            if option == correct_option:
                st.success("✅ सही उत्तर")
                st.session_state.score += 1
            else:
                st.error(f"❌ सही उत्तर: {correct_option}")

            st.session_state.current += 1
            st.rerun()

    else:

        st.balloons()

        st.success("🎉 Quiz Completed!")

        score = st.session_state.score
        total = len(mcqs)

        percent = (score / total) * 100

        st.metric("Score", f"{score}/{total}")
        st.metric("Percentage", f"{percent:.1f}%")

        if percent >= 90:
            st.success("🏆 Gold Rank")
        elif percent >= 70:
            st.info("🥈 Silver Rank")
        elif percent >= 50:
            st.warning("🥉 Bronze Rank")
        else:
            st.error("📚 Practice More")

        if st.button("🔄 Restart Quiz"):

            del st.session_state.current
            del st.session_state.score
            del st.session_state.mcqs

            st.rerun()
