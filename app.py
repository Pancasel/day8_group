import streamlit as st
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Cấu hình đường dẫn và load env
load_dotenv()
sys.path.insert(0, str(Path(__file__).parent))

# Import từ các task cá nhân
from src.task9_retrieval_pipeline import retrieve
from src.task10_generation import reorder_for_llm, format_context, SYSTEM_PROMPT, TEMPERATURE, TOP_P

# Thiết lập trang Streamlit
st.set_page_config(
    page_title="RAG Chatbot - Luật Ma Túy & Nghệ Sĩ",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Cấu hình stdout hiển thị UTF-8 tránh lỗi in trên Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Custom CSS cho giao diện cao cấp
st.markdown(
    """
    <style>
    /* Nhập font chữ Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    html, body, .stApp {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Style cho tiêu đề chính */
    .main-title {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #FF6B6B 0%, #FFD93D 50%, #4D96FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    
    .subtitle {
        text-align: center;
        color: #8A8F98;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        font-weight: 300;
    }

    /* Bo góc và làm đẹp cho các khối Expander tài liệu nguồn */
    .streamlit-expanderHeader {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 8px !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
    }
    
    .streamlit-expanderContent {
        background-color: rgba(255, 255, 255, 0.01) !important;
        border-left: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-bottom-left-radius: 8px !important;
        border-bottom-right-radius: 8px !important;
        padding: 1rem !important;
    }
    
    /* Thiết kế nhãn loại nguồn (tag) */
    .source-tag {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        margin-left: 10px;
    }
    .tag-legal {
        background-color: rgba(77, 150, 255, 0.15);
        color: #4D96FF;
        border: 1px solid rgba(77, 150, 255, 0.3);
    }
    .tag-news {
        background-color: rgba(255, 107, 107, 0.15);
        color: #FF6B6B;
        border: 1px solid rgba(255, 107, 107, 0.3);
    }
    .tag-fallback {
        background-color: rgba(255, 217, 61, 0.15);
        color: #FFD93D;
        border: 1px solid rgba(255, 217, 61, 0.3);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header giao diện
st.markdown("<h1 class='main-title'>⚖️ DrugLaw RAG Chatbot</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Hỏi đáp thông minh về Luật ma túy và Tin tức nghệ sĩ liên quan</p>", unsafe_allow_html=True)

# Khởi tạo OpenAI Client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("⚠️ Không tìm thấy `OPENAI_API_KEY` trong file `.env`! Vui lòng bổ sung để sử dụng Chatbot.")
    st.stop()

from openai import OpenAI
client = OpenAI(api_key=api_key)

# Khởi tạo lịch sử chat trong session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị lịch sử chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Nếu là chatbot phản hồi và có tài liệu nguồn, hiển thị nguồn
        if message["role"] == "assistant" and "sources" in message and message["sources"]:
            st.write("---")
            st.markdown("**🔍 Nguồn tài liệu tham khảo:**")
            for i, chunk in enumerate(message["sources"], 1):
                source = chunk.get("metadata", {}).get("source", f"Source {i}")
                doc_type = chunk.get("metadata", {}).get("type", "unknown")
                score = chunk.get("score", 0.0)
                ret_source = chunk.get("source", "hybrid")
                
                # Xác định css class cho tag loại tài liệu
                tag_class = "tag-legal" if doc_type == "legal" else "tag-news"
                if ret_source == "pageindex":
                    tag_class = "tag-fallback"
                    
                expander_label = f"[{i}] {source} (Score: {score:.3f})"
                
                with st.expander(expander_label):
                    st.markdown(
                        f"**Loại tài liệu:** <span class='source-tag {tag_class}'>{doc_type}</span> "
                        f"| **Phương thức:** `{ret_source}`", 
                        unsafe_allow_html=True
                    )
                    st.markdown(f"\n{chunk['content']}")

# Tiếp nhận chat input từ người dùng
if prompt := st.chat_input("Nhập câu hỏi của bạn tại đây..."):
    # 1. Hiển thị câu hỏi của người dùng và lưu vào session
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Xử lý phản hồi từ RAG
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        
        # Gọi Retrieval Pipeline để lấy các đoạn văn bản liên quan nhất
        with st.spinner("Đang tìm kiếm thông tin và phân tích nguồn..."):
            chunks = retrieve(prompt, top_k=5)
            
            # Sắp xếp lại chunks tránh hiện tượng Lost in the Middle
            reordered_chunks = reorder_for_llm(chunks)
            context = format_context(reordered_chunks)

        # Xây dựng hội thoại truyền cho LLM bao gồm cả lịch sử chat (Conversation Memory)
        messages_for_llm = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # Thêm các câu chat lịch sử (giới hạn 6 lượt gần nhất để tránh tràn context)
        for msg in st.session_state.messages[-7:-1]:
            messages_for_llm.append({"role": msg["role"], "content": msg["content"]})
            
        # Thêm câu hỏi hiện tại kèm theo ngữ cảnh vừa tìm kiếm
        user_message_with_context = f"Context:\n{context}\n\n---\n\nQuestion: {prompt}"
        messages_for_llm.append({"role": "user", "content": user_message_with_context})

        # Gọi OpenAI để sinh phản hồi
        try:
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages_for_llm,
                temperature=TEMPERATURE,
                top_p=TOP_P,
                stream=True
            )
            
            full_response = ""
            for response in stream:
                if response.choices[0].delta.content:
                    full_response += response.choices[0].delta.content
                    response_placeholder.markdown(full_response + "▌")
            response_placeholder.markdown(full_response)
            
        except Exception as e:
            full_response = f"Lỗi trong quá trình kết nối LLM: {str(e)}"
            response_placeholder.markdown(full_response)

        # Hiển thị các tài liệu nguồn tham khảo
        if chunks:
            st.write("---")
            st.markdown("**🔍 Nguồn tài liệu tham khảo:**")
            for i, chunk in enumerate(chunks, 1):
                source = chunk.get("metadata", {}).get("source", f"Source {i}")
                doc_type = chunk.get("metadata", {}).get("type", "unknown")
                score = chunk.get("score", 0.0)
                ret_source = chunk.get("source", "hybrid")
                
                tag_class = "tag-legal" if doc_type == "legal" else "tag-news"
                if ret_source == "pageindex":
                    tag_class = "tag-fallback"
                    
                expander_label = f"[{i}] {source} (Score: {score:.3f})"
                
                with st.expander(expander_label):
                    st.markdown(
                        f"**Loại tài liệu:** <span class='source-tag {tag_class}'>{doc_type}</span> "
                        f"| **Phương thức:** `{ret_source}`", 
                        unsafe_allow_html=True
                    )
                    st.markdown(f"\n{chunk['content']}")

        # Lưu phản hồi kèm theo nguồn tài liệu vào session state
        st.session_state.messages.append({
            "role": "assistant",
            "content": full_response,
            "sources": chunks
        })
