import streamlit as st
import base64
from datetime import datetime
from core import PlantDiseaseDetector
from chatbot import PlantDiseaseChatbot

# Constants
DISEASE_TYPE_INVALID = "invalid_image"

# Set Streamlit theme to light and wide mode
st.set_page_config(
    page_title="Phát Hiện Bệnh Trên Cây",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for chatbot
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = None
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
if 'disease_result' not in st.session_state:
    st.session_state.disease_result = None
if 'show_chat_dialog' not in st.session_state:
    st.session_state.show_chat_dialog = False
# Initialize session state for uploaded images history
if 'uploaded_images' not in st.session_state:
    st.session_state.uploaded_images = []
if 'confirm_clear_history' not in st.session_state:
    st.session_state.confirm_clear_history = False

# --- SIDEBAR (THANH BÊN) ---
with st.sidebar:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("black-tree-logo.png", width=100)
    st.title("Developing an AI Application")
    st.info("""
    Hệ thống đánh giá, phân tích và phát hiện bệnh dựa trên hình ảnh lá, rễ, và thân cây nhờ vào Computer Vision và Machine Learning.
    Đồng thời cung cấp các thông tin về triệu chứng, nguyên nhân và biện pháp xử lí.
    """)

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
    
    /* ===== FLOATING CHATBOT ===== */
    .chatbot-float-btn {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #2E7D32 0%, #1B5E20 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 12px rgba(46, 125, 50, 0.4);
        cursor: pointer;
        z-index: 9999;
        transition: all 0.3s ease;
    }
    
    .chatbot-float-btn:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 20px rgba(46, 125, 50, 0.6);
    }
    
    .chatbot-float-btn svg {
        width: 32px;
        height: 32px;
        fill: white;
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
        <h1 style='color: #1565c0; margin-bottom: 0; font-size: 3em'>ỨNG DỤNG AI PHÁT HIỆN BỆNH TRÊN CÂY</h1>
        <p style='color: #616161; font-size: 1.15em;'>Tải ảnh lá, rễ, hoặc thân cây để phát hiện bệnh và nhận lời khuyên</p>
    </div>
""", unsafe_allow_html=True)

# ========== DISEASE DETECTION SECTION ==========
st.markdown("## 🔍 Phân tích")
uploaded_file = st.file_uploader(
    "Tải ảnh bộ phận cây (lá, rễ, thân)", type=["jpg", "jpeg", "png"], key="file_uploader")

if uploaded_file is not None:
    if st.button("🔍 Phân tích bệnh", use_container_width=True, key="analyze_btn"):
        with st.spinner("Đang phân tích..."):
            try:
                # ✅ GỌI TRỰC TIẾP (KHÔNG QUA API)
                detector = PlantDiseaseDetector()
                
                # Convert image to base64
                image_bytes = uploaded_file.getvalue()
                base64_image = base64.b64encode(image_bytes).decode('utf-8')
                
                # Phân tích
                result = detector.analyze_plant_image_base64(base64_image)
                
                # Save result to session state for chatbot
                st.session_state.disease_result = result
                
                # Save uploaded image to history with metadata
                image_record = {
                    'filename': uploaded_file.name,
                    'image_base64': base64_image,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'result': result
                }
                st.session_state.uploaded_images.append(image_record)
                
                # Automatically send context to chatbot
                if st.session_state.chatbot is None:
                    st.session_state.chatbot = PlantDiseaseChatbot()
                st.session_state.chatbot.set_disease_context(result)
                
                # Ensure chatbot dialog is closed
                st.session_state.show_chat_dialog = False
                
            except Exception as e: 
                st.error(f"Lỗi: {str(e)}")
                import traceback
                st.code(traceback.format_exc())

# Display results if available (outside button click so it persists)
if st.session_state.disease_result is not None:
    result = st.session_state.disease_result
    
    # Check if it's an invalid image
    if result.get("disease_type") == DISEASE_TYPE_INVALID:
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
                Vui lòng tải lại hình ảnh của bộ phận cây (lá, rễ, thân).
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
        # Healthy plant case
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

# ========== IMAGE HISTORY SECTION ==========

st.markdown("---")
st.markdown("## 📁 Lịch sử hình ảnh đã tải")
if st.session_state.uploaded_images:
    # Add clear history button with confirmation
    if not st.session_state.confirm_clear_history:
        if st.button("🗑️ Xóa lịch sử", key="clear_history"):
            st.session_state.confirm_clear_history = True
            st.session_state.uploaded_images = []
            st.session_state.confirm_clear_history = False
    
    # Display in reverse order (most recent first)
    for idx, img_record in enumerate(reversed(st.session_state.uploaded_images)):
        with st.expander(f"🖼️ {img_record['filename']} - {img_record['timestamp']}", expanded=False):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Decode base64 image for display
                image_bytes = base64.b64decode(img_record['image_base64'])
                st.image(image_bytes, caption=img_record['filename'], use_container_width=True)
                
                # Add chatbot button for this image's analysis
                if st.button("💬 Hỏi Chatbot về ảnh này", key=f"chat_btn_{idx}", type="secondary", use_container_width=True):
                    # Initialize chatbot if not exists
                    if st.session_state.chatbot is None:
                        st.session_state.chatbot = PlantDiseaseChatbot()
                    # Set the disease context to this image's result
                    st.session_state.chatbot.set_disease_context(img_record['result'])
                    # Open chatbot dialog
                    st.session_state.show_chat_dialog = True
                    st.rerun()
            
            with col2:
                result = img_record['result']
                
                # Display detailed results based on result type
                if result.get("disease_type") == DISEASE_TYPE_INVALID:
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
                        <div class="result-card invalid" style="margin-top: 0;">

                        <div class="disease-title">⚠️ Ảnh không hợp lệ</div>

                        <div style="color:#ff5722; font-size:1.05em; margin-bottom: 1em;">
                            Vui lòng tải lại hình ảnh của bộ phận cây (lá, rễ, thân).
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
                        <div class="result-card" style="margin-top: 0;">

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
                    # Healthy plant case
                    st.markdown(
                        f"""
                        <div class="result-card" style="margin-top: 0;">

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

# ========== FLOATING CHATBOT WIDGET ==========

# Initialize chatbot if not exists
if st.session_state.chatbot is None:
    try:
        st.session_state.chatbot = PlantDiseaseChatbot()
    except Exception as e:
        st.error(f"Không thể khởi tạo chatbot: {str(e)}")

# Use dialog for chat interface
@st.dialog("💬 Chatbot Tư vấn", width="large")
def show_chatbot():
    # Header with clear button
    col1, col2 = st.columns([2, 1], vertical_alignment="center")
    with col1:
        if st.session_state.disease_result:
            st.success("✅ Chatbot đã có thông tin phân tích bệnh")
        else:
            st.info("💡 Hãy phân tích ảnh bộ phận cây (lá, rễ, thân) trước để chatbot có thể tư vấn chi tiết!")
    with col2:
        if st.button("🗑️", key="clear_chat_dlg", help="Xóa lịch sử chat"):
            st.session_state.chat_messages = []
            if st.session_state.chatbot is not None:
                st.session_state.chatbot.clear_history()
            st.rerun()
    
    # Chat messages container
    chat_container = st.container(height=450)
    with chat_container:
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Nhập câu hỏi...", key="chat_dlg_input"):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        
        try:
            response = st.session_state.chatbot.chat(prompt)
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
        except Exception as e:
            error_msg = f"Xin lỗi, đã có lỗi: {str(e)}"
            st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})
        
        # Rerun to show new messages (dialog stays open automatically)
        st.rerun()

# Show dialog if flag is set
if st.session_state.show_chat_dialog:
    show_chatbot()

# Add floating chatbot button with truly fixed positioning using st.html()
st.html("""
    <style>
    /* Ensure button stays fixed at bottom-right even when scrolling */
    #chatbot-fab {
        position: fixed !important;
        bottom: 20px !important;
        right: 20px !important;
        z-index: 9999 !important;
        width: 60px !important;
        height: 60px !important;
        border-radius: 50% !important;
        background: linear-gradient(135deg, #43a047 0%, #2e7d32 100%) !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(46, 125, 50, 0.4) !important;
        cursor: pointer !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 24px !important;
        transition: all 0.3s ease !important;
    }
    
    #chatbot-fab:hover {
        transform: scale(1.1) !important;
        box-shadow: 0 6px 20px rgba(46, 125, 50, 0.6) !important;
    }
    
    /* Hide default streamlit button styling for the chatbot FAB */
    div[data-testid="stVerticalBlock"] > div:last-child button[kind="primary"] {
        position: fixed !important;
        bottom: 60px !important;
        right: 20px !important;
        z-index: 9999 !important;
        width: 50px !important;
        height: 50px !important;
        border-radius: 50% !important;
        padding: 0 !important;
        min-height: 50px !important;
        font-size: 24px !important;
        transform: scale(1.2) !important;
    }
    </style>
""")

# Floating chatbot button
if st.button("💬", key="open_chatbot", help="", type="primary"):
    st.session_state.show_chat_dialog = True
    st.rerun()