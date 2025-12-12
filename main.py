import streamlit as st
import base64
from core import LeafDiseaseDetector
from chatbot import PlantDiseaseChatbot

# Set Streamlit theme to light and wide mode
st.set_page_config(
    page_title="Leaf Disease Detection",
    page_icon="🌿",
    layout="wide",                         # Dùng giao diện rộng
    initial_sidebar_state="expanded"
)

# Initialize session state for chatbot
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = None
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []

# --- SIDEBAR (THANH BÊN) ---
with st.sidebar:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("black-tree-logo.png", width=100)
    st.title("Thông tin Dự án")
    st.info("""
    **Project 2: Developing an AI Application**
            
    Môn: Introduction to Artificial Intelligence
    """)
    
    st.markdown("---")
    st.subheader("👥 Thành viên nhóm")
    st.write("1. Hà Chí Tâm - 25122039")
    st.write("2. Ngô Phạm Hồng Thức - 25122044")
    st.write("3. Huỳnh Văn Phú - 25122036")
    
    st.markdown("---")
    st.caption("Model: The Llama 4")
    st.caption("Framework: Hugging Face, Groq & Streamlit")
    
    st.markdown("---")
    st.subheader("🤖 Chế độ")
    app_mode = st.radio(
        "Chọn chức năng:",
        ["🔍 Phát hiện bệnh", "💬 Chatbot tư vấn"],
        label_visibility="collapsed"
    )

st.markdown("""
    <style>
    /* ===== RESULT CARD ===== */
    .result-card{
    background: rgba(255,255,255,0.97);
    border-radius: 18px;
    padding: 2em 2em 1.8em;
    margin-top: 1.8em;
    box-shadow: 0 8px 28px rgba(27,94,32,0.10);
    border: 1px solid rgba(46,125,50,0.18);
    }

    /* Header */
    .result-header{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1em;
    }

    .disease-title{
    font-size: 2em;
    font-weight: 800;
    color: #2E7D32;
    }

    /* Severity badge */
    .severity{
    padding: 0.35em 0.9em;
    border-radius: 999px;
    font-size: 0.95em;
    font-weight: 700;
    white-space: nowrap;
    }

    .severity.low{
    background: #E8F5E9;
    color: #2E7D32;
    }

    .severity.medium{
    background: #FFF8E1;
    color: #F9A825;
    }

    .severity.high{
    background: #FDECEA;
    color: #C62828;
    }

    /* Section titles */
    .section-title{
    font-size: 1.15em;
    font-weight: 700;
    color: #1B5E20;
    margin-top: 1.1em;
    margin-bottom: 0.4em;
    }

    /* Lists */
    .result-list{
    margin-left: 1.1em;
    color: #3E4A41;
    }

    .result-list li{
    margin-bottom: 0.3em;
    }

    /* Footer info */
    .confidence{
    margin-top: 1.2em;
    font-size: 0.95em;
    color: #5F6F64;
    }
</style>
""", unsafe_allow_html=True)

with open("agriculture.png", "rb") as f:
    logo = base64.b64encode(f.read()).decode()
logo_html = f'<img src="data:image/png;base64,{logo}" class="header-logo">'

st.markdown(
        f"""<div style="text-align: center; margin: 0.2em auto; margin-bottom: 0; max-width: 105px;">
            {logo_html}
        </div>
""", unsafe_allow_html=True)

st.markdown("""
    <div style='text-align: center; margin-top: 0.1em;'>
        <h1 style='color: #1565c0; margin-bottom: 0; font-size: 2.5em'>PHÁT HIỆN BỆNH LÁ</h1>
        <p style='color: #616161; font-size: 1.15em;'>Tải ảnh lá để phát hiện bệnh và nhận lời khuyên</p>
    </div>
""", unsafe_allow_html=True)

# Check which mode is selected
if app_mode == "🔍 Phát hiện bệnh":
    # Original disease detection UI
    col1, col2 = st.columns([1, 2])
    with col1:
        uploaded_file = st.file_uploader(
            "Tải ảnh", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None: 
            st.image(uploaded_file, caption="Xem")

    with col2:
        if uploaded_file is not None:
            if st.button("🔍 Phân tích", use_container_width=True):
                with st.spinner("Đang phân tích..."):
                    try:
                        # ✅ GỌI TRỰC TIẾP (KHÔNG QUA API)
                        detector = LeafDiseaseDetector()
                        
                        # Convert image to base64
                        image_bytes = uploaded_file.getvalue()
                        base64_image = base64.b64encode(image_bytes).decode('utf-8')
                        
                        # Phân tích
                        result = detector.analyze_leaf_image_base64(base64_image)

                        # Check if it's an invalid image
                        if result. get("disease_type") == "invalid_image":
                            symptoms = result.get("symptoms", []) or []
                            treatments = result.get("treatment", []) or []

                            symptoms_html = ""
                            if symptoms:
                                symptoms_html = f"""
                                <div class="section-title">Vấn đề</div>
                                <ul class="symptom-list">
                                {''.join(f"<li>{s}</li>" for s in symptoms)}
                                </ul>
                                """

                            treatments_html = ""
                            if treatments:
                                treatments_html = f"""
                                <div class="section-title">Lời khuyên</div>
                                <ul class="treatment-list">
                                {''.join(f"<li>{t}</li>" for t in treatments)}
                                </ul>
                                """

                            st.markdown(
                                f"""
                                <div class="result-card invalid">

                                <div class="disease-title">⚠️ Ảnh không hợp lệ</div>

                                <div style="color:#ff5722; font-size:1.05em; margin-bottom: 1em;">
                                    Vui lòng tải lại hình ảnh của lá cây.
                                </div>

                                {symptoms_html}
                                {treatments_html}

                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                        elif result.get("disease_detected"):
                            st.markdown(
                                f"""
                                <div class="result-card">

                                <div class="disease-title">
                                    🦠 {result.get('disease_name', 'N/A')}
                                </div>

                                <div style="margin-bottom: 0.8em;">
                                    <div class="info-badge">Loại: {result.get('disease_type', 'N/A')}</div>
                                    <div class="info-badge">Mức độ: {result.get('severity', 'N/A')}</div>
                                    <div class="info-badge">Độ tin cậy: {result.get('confidence', 'N/A')}%</div>
                                </div>

                                <div class="section-title">Triệu chứng</div>
                                <ul class="symptom-list">
                                    {''.join(f"<li>{s}</li>" for s in result.get("symptoms", []))}
                                </ul>

                                <div class="section-title">Nguyên nhân</div>
                                <ul class="cause-list">
                                    {''.join(f"<li>{c}</li>" for c in result.get("possible_causes", []))}
                                </ul>

                                <div class="section-title">Biện pháp xử lý</div>
                                <ul class="treatment-list">
                                    {''.join(f"<li>{t}</li>" for t in result.get("treatment", []))}
                                </ul>

                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                        else:
                            # Healthy leaf case
                            st.markdown(
                                f"""
                                <div class="result-card">

                                <div class="disease-title">✅ Cây khoẻ mạnh</div>

                                <div style="
                                    color: #4caf50;
                                    font-size: 1.1em;
                                    margin-bottom: 1em;
                                ">
                                    Không phát hiện bệnh trên lá cây
                                </div>

                                <div class="info-badge">
                                    🌱 Tình trạng: {result.get('disease_type', 'healthy')}
                                </div>

                                <div class="info-badge">
                                    🔬 Đáng tin cậy: {result.get('confidence', 'N/A')}%
                                </div>

                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                            
                    except Exception as e: 
                        st.error(f"Lỗi: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())

else:  # Chatbot mode
    st.markdown("### 💬 Chatbot Tư Vấn Bệnh Cây")
    st.markdown("*Hỏi tôi bất cứ điều gì về bệnh cây trồng, triệu chứng, cách điều trị...*")
    
    # Initialize chatbot if not exists
    if st.session_state.chatbot is None:
        try:
            st.session_state.chatbot = PlantDiseaseChatbot()
        except Exception as e:
            st.error(f"Không thể khởi tạo chatbot: {str(e)}")
            st.stop()
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Nhập câu hỏi của bạn..."):
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Add to session state
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        
        # Get chatbot response
        with st.chat_message("assistant"):
            with st.spinner("Đang suy nghĩ..."):
                try:
                    response = st.session_state.chatbot.chat(prompt)
                    st.markdown(response)
                    st.session_state.chat_messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"Xin lỗi, đã có lỗi xảy ra: {str(e)}"
                    st.error(error_msg)
                    st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})
    
    # Clear chat button
    if st.button("🔄 Xóa lịch sử chat", use_container_width=True):
        st.session_state.chat_messages = []
        if st.session_state.chatbot:
            st.session_state.chatbot.clear_history()
        st.rerun()