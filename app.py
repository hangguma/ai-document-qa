import streamlit as st
from anthropic import Anthropic
import pypdf

# Claude Sonnet 4.6 pricing (USD per million tokens), as of 2026-07.
# Pricing is per-model and not exposed via API — verify at
# https://platform.claude.com/docs/en/pricing when changing the model below.
PRICE_PER_M_INPUT = 3.00
PRICE_PER_M_OUTPUT = 15.00
PRICING_AS_OF = "2026-07"

# Page configuration
st.set_page_config(
    page_title="AI Document Q&A",
    page_icon="🤖",
    layout="wide"
)

# Title and description
st.title("🤖 AI Document Q&A System")
st.markdown("Upload a PDF document and ask questions about its content using Claude AI")
st.markdown("---")

# API key handling
# Deployment: Use Streamlit secrets
# Local: Use sidebar input
try:
    api_key = st.secrets["ANTHROPIC_API_KEY"]
    st.sidebar.success("✅ API Key Connected")
except:
    with st.sidebar:
        st.header("⚙️ Settings")
        api_key = st.text_input(
            "Claude API Key", 
            type="password",
            help="Get your API key from https://platform.claude.com"
        )
        
        if api_key:
            st.success("✅ API Key Entered")
        else:
            st.warning("⚠️ Please enter your API key")

# Add info sidebar
with st.sidebar:
    st.markdown("---")
    st.markdown("### 📖 About")
    st.markdown("""
    This application uses Claude AI to answer questions about your PDF documents.
    
    **Features:**
    - PDF text extraction
    - AI-powered Q&A
    - Natural language processing
    
    **Tech Stack:**
    - Streamlit
    - Claude API
    - pypdf
    """)
    
    st.markdown("---")
    st.markdown("### 🔗 Links")
    st.markdown("[GitHub](https://github.com/hangguma/ai-document-qa)")
    st.markdown("[Live Demo](https://ai-document-q-a.streamlit.app)")

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    # PDF upload
    uploaded_file = st.file_uploader(
        "📄 Upload your PDF document", 
        type=['pdf'],
        help="Select a PDF file to analyze"
    )

with col2:
    if uploaded_file:
        st.metric(
            label="Document Status",
            value="Ready",
            delta="Uploaded"
        )

# PDF text extraction
if uploaded_file:
    try:
        # Read PDF
        pdf_reader = pypdf.PdfReader(uploaded_file)
        
        # Extract all text
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        # Document preview
        with st.expander("📖 Document Preview (First 500 characters)"):
            st.text(text[:500] + "...")
        
        st.success(f"✅ Document loaded successfully! ({len(pdf_reader.pages)} pages)")
        
        # Question input
        st.markdown("---")
        st.subheader("💬 Ask a Question")
        
        question = st.text_input(
            "Enter your question about the document:",
            placeholder="e.g., What is the main topic of this document?"
        )
        
        # Answer generation
        if question and api_key:
            col1, col2, col3 = st.columns([1, 1, 3])
            with col1:
                generate_button = st.button("🚀 Get Answer", type="primary", use_container_width=True)
            with col2:
                if st.button("🔄 Clear", use_container_width=True):
                    st.rerun()
            
            if generate_button:
                with st.spinner("🤔 Claude is thinking..."):
                    try:
                        # Call Claude API
                        client = Anthropic(api_key=api_key)
                        
                        message = client.messages.create(
                            model="claude-sonnet-4-6",
                            max_tokens=1024,
                            messages=[{
                                "role": "user",
                                "content": f"""Please read the following document and answer the question based on its content.

Document Content:
{text[:3000]}

Question: {question}

Please provide an accurate answer based solely on the information in the document. If the answer cannot be found in the document, please state that clearly."""
                            }]
                        )
                        
                        # Display answer
                        st.markdown("---")
                        st.markdown("### 🤖 Claude's Answer:")
                        
                        # Answer box with nice formatting
                        st.info(message.content[0].text)
                        
                        # Cost calculation
                        input_cost = message.usage.input_tokens / 1_000_000 * PRICE_PER_M_INPUT
                        output_cost = message.usage.output_tokens / 1_000_000 * PRICE_PER_M_OUTPUT
                        query_cost = input_cost + output_cost

                        # Track cumulative session cost
                        st.session_state.total_cost = st.session_state.get("total_cost", 0.0) + query_cost
                        st.session_state.query_count = st.session_state.get("query_count", 0) + 1

                        # Additional info
                        with st.expander("ℹ️ Response Details"):
                            st.write(f"**Model:** {message.model}")
                            st.write(f"**Tokens Used:** {message.usage.input_tokens} input, {message.usage.output_tokens} output")
                            st.write(
                                f"**Cost:** \\${query_cost:.6f} "
                                f"(input \\${input_cost:.6f} + output \\${output_cost:.6f})"
                            )
                            st.write(
                                f"**Session Total:** \\${st.session_state.total_cost:.6f} "
                                f"across {st.session_state.query_count} "
                                f"{'query' if st.session_state.query_count == 1 else 'queries'}"
                            )
                            st.caption(
                                "Every question re-sends the document as input tokens — "
                                "the document is the recurring cost, not the question."
                            )
                            st.caption(
                                f"Cost is an estimate based on Claude Sonnet 4.6 pricing "
                                f"as of {PRICING_AS_OF}: \\${PRICE_PER_M_INPUT:.2f} input / "
                                f"\\${PRICE_PER_M_OUTPUT:.2f} output per 1M tokens. "
                                f"Actual billing may differ — see the "
                                f"[official pricing page](https://platform.claude.com/docs/en/pricing)."
                            )
                        
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        st.info("💡 Tip: Check your API key and try again")
        
        elif question and not api_key:
            st.warning("⚠️ Please enter your API key in the sidebar first!")
            
    except Exception as e:
        st.error(f"❌ Error reading PDF: {str(e)}")
        st.info("💡 Tip: Make sure your PDF is not encrypted or corrupted")
else:
    # Welcome message when no file is uploaded
    st.info("👆 Please upload a PDF document to get started")
    
    # Example use cases
    st.markdown("### 🎯 Example Use Cases")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **📚 Research Papers**
        - Summarize key findings
        - Extract methodology
        - Find specific data
        """)
    
    with col2:
        st.markdown("""
        **📋 Reports**
        - Answer specific questions
        - Extract statistics
        - Find recommendations
        """)
    
    with col3:
        st.markdown("""
        **📄 Documents**
        - Understand content
        - Find information
        - Get insights
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Built with ❤️ using Streamlit and Claude AI</p>
    <p>
        <a href="https://github.com/hangguma/ai-document-qa" target="_blank">GitHub</a> | 
        <a href="https://platform.claude.com" target="_blank">Claude API</a> | 
        <a href="https://streamlit.io" target="_blank">Streamlit</a>
    </p>
</div>
""", unsafe_allow_html=True)