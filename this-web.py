import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai
import time
from openai import RateLimitError

st.set_page_config(page_title="GPT 단일 웹페이지 요약기", layout="wide")

# ✅ OpenAI 클라이언트
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("📄 GPT 단일 웹페이지 요약기")
st.write("입력한 웹페이지의 **해당 본문만** 요약해드립니다. (하위 링크 미포함)")

# ✅ 본문 추출 함수
def extract_text(url):
    try:
        res = requests.get(url, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
        for tag in soup(['script', 'style', 'header', 'footer', 'nav']):
            tag.decompose()
        return soup.get_text(separator=' ', strip=True)
    except Exception as e:
        st.warning(f"본문 추출 실패: {e}")
        return ""

# ✅ 요약 함수 (자동 재시도 포함)
def summarize_text(text):
    prompt = f"다음 웹 페이지 내용을 핵심만 요약해줘:\n{text}"
    for i in range(3):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
            return response.choices[0].message.content
        except RateLimitError:
            wait = 2 ** i
            st.warning(f"요청이 많아 대기 중입니다... ({wait}초)")
            time.sleep(wait)
        except Exception as e:
            return f"요약 실패: {e}"
    return "❌ 요약 실패: 너무 많은 요청입니다. 잠시 후 다시 시도해주세요."

# ✅ 입력
url = st.text_input("🔗 웹페이지 주소 입력", placeholder="https://example.com")

if st.button("요약 시작") and url:
    with st.spinner("📄 본문 수집 중..."):
        text = extract_text(url)[:8000]  # token 제한
    with st.spinner("🧠 GPT 요약 중..."):
        summary = summarize_text(text)

    st.subheader("📋 요약 결과")
    st.write(summary)
    st.download_button("📥 요약 결과 다운로드", summary, file_name="summary.txt")
