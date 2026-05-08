import streamlit as st
from anthropic import Anthropic
import pypdf

# 페이지 설정
st.set_page_config(page_title="AI 문서 Q&A", page_icon="🤖")

# 제목
st.title("🤖 AI 문서 질의응답 시스템")
st.markdown("---")

# API 키 가져오기
# 배포 시: Streamlit secrets 사용
# 로컬 시: 사이드바 입력
try:
    api_key = st.secrets["ANTHROPIC_API_KEY"]
    st.sidebar.success("✅ API 키 연결됨")
except:
    with st.sidebar:
        st.header("⚙️ 설정")
        api_key = st.text_input(
            "Claude API Key", 
            type="password",
            help="https://platform.claude.com 에서 발급받으세요"
        )
        
        if api_key:
            st.success("✅ API 키 입력됨")
        else:
            st.warning("⚠️ API 키를 입력하세요")

# PDF 업로드
uploaded_file = st.file_uploader(
    "📄 PDF 파일을 업로드하세요", 
    type=['pdf']
)

# PDF 텍스트 추출
if uploaded_file:
    try:
        # PDF 읽기
        pdf_reader = pypdf.PdfReader(uploaded_file)
        
        # 전체 텍스트 추출
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        # 텍스트 미리보기
        with st.expander("📖 문서 미리보기"):
            st.text(text[:500] + "...")
        
        st.success(f"✅ PDF 로드 완료! (총 {len(pdf_reader.pages)}페이지)")
        
        # 질문 입력
        st.markdown("---")
        question = st.text_input("💬 질문을 입력하세요:")
        
        # 답변 생성
        if question and api_key:
            if st.button("🚀 답변 받기", type="primary"):
                with st.spinner("AI가 생각 중..."):
                    try:
                        # Claude API 호출
                        client = Anthropic(api_key=api_key)
                        
                        message = client.messages.create(
                            model="claude-sonnet-4-6",
                            max_tokens=1024,
                            messages=[{
                                "role": "user",
                                "content": f"""다음 문서를 읽고 질문에 답변해주세요.

문서 내용:
{text[:3000]}

질문: {question}

답변은 한국어로, 문서 내용을 기반으로 정확하게 답변해주세요."""
                            }]
                        )
                        
                        # 답변 표시
                        st.markdown("### 🤖 AI 답변:")
                        st.write(message.content[0].text)
                        
                    except Exception as e:
                        st.error(f"❌ 오류 발생: {str(e)}")
        
        elif question and not api_key:
            st.warning("⚠️ API 키를 먼저 입력하세요!")
            
    except Exception as e:
        st.error(f"❌ PDF 읽기 오류: {str(e)}")
else:
    st.info("👆 PDF 파일을 업로드해주세요")