import streamlit as st
import fitz  # PyMuPDF
from openai import OpenAI
import openai.error
import time

# GPT 클라이언트 초기화
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# PDF 텍스트 추출
def extract_text_from_pdf(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# GPT 요약 (예외 처리 포함)
def summarize_text_with_retry(prompt, retries=3):
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            return response.choices[0].message.content
        except openai.RateLimitError:
            time.sleep(5)
    return "요청 실패: Rate Limit 초과"

# 텍스트 분할
def split_text_by_length(text, max_length=3000):
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

# 전체 요약 파이프라인
def summarize_large_text(text):
    chunks = split_text_by_length(text)
    partial_summaries = []

    for idx, chunk in enumerate(chunks):
        st.info(f"문서 요약 중... ({idx+1}/{len(chunks)})")
        prompt = f"""
        다음 문서를 핵심만 요약해줘. 구조화된 형식으로 정리해줘.

        문서:
        {chunk}

        형식:
        - 요약:
        - 주요 항목:
        - 질문:
        """
        summary = summarize_text_with_retry(prompt)
        partial_summaries.append(summary)

    # 전체 통합 요약
    final_prompt = f"""
    아래는 문서 일부 요약들이야. 이걸 종합해서 전체 문서를 요약해줘:

    {'\n\n'.join(partial_summaries)}

    형식:
    - 문서 전체 요약:
    - 핵심 항목 정리:
    - 생각해볼 질문:
    """
    final_summary = summarize_text_with_retry(final_prompt)
    return final_summary

# Streamlit UI
st.set_page_config(page_title="GPT 기반 PDF 요약", layout="wide")
st.title("📄 GPT 기반 PDF 요약 서비스")
st.write("업로드한 PDF 문서를 GPT가 자동으로 요약해드립니다.")

uploaded_file = st.file_uploader("PDF 파일을 업로드해주세요", type=["pdf"])

if uploaded_file is not None:
    with st.spinner("PDF 처리 중..."):
        extracted_text = extract_text_from_pdf(uploaded_file)
        final_summary = summarize_large_text(extracted_text)
        st.success("요약 완료!")
        st.markdown("### 📝 요약 결과")
        st.text_area("문서 요약", final_summary, height=500)
