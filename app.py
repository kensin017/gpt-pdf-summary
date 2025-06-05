import streamlit as st
import fitz  # PyMuPDF
import openai
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def extract_text_from_pdf(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def summarize_text(text):
    prompt = f"""
    아래 문서를 요약해줘. 핵심 항목 위주로 구조화된 포맷으로 정리해줘.

    문서:
    {text[:3000]}

    결과 형식:
    - 문서 요약:
    - 주요 항목:
    - 주요 질문:
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content

# Streamlit UI
st.title("📄 GPT 기반 PDF 요약 서비스")
st.write("업로드한 문서를 자동으로 요약해드립니다.")

uploaded_file = st.file_uploader("PDF 파일을 업로드해주세요", type=["pdf"])

if uploaded_file is not None:
    with st.spinner("문서 요약 중..."):
        extracted_text = extract_text_from_pdf(uploaded_file)
        summary = summarize_text(extracted_text)
        st.success("요약 완료!")
        st.markdown("### 📝 요약 결과")
        st.text_area("요약 내용", summary, height=400)
