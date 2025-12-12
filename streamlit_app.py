import streamlit as st
import requests

# Set Streamlit theme to light and wide mode
st.set_page_config(
    page_title="Leaf Disease Detection",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# Enhanced modern CSS
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #e3f2fd 0%, #f7f9fa 100%);
    }
    .result-card {
        # background: rgba(255,255,255,0.95);
        # border-radius: 18px;
        # box-shadow: 0 4px 24px rgba(44,62,80,0.10);
        # padding: 2.5em 2em;
        # margin-top: 1.5em;
        # margin-bottom: 1.5em;
        # transition: box-shadow 0.3s;
    }
    .result-card:hover {
        box-shadow: 0 8px 32px rgba(44,62,80,0.18);
    }
    .disease-title {
        color: #1b5e20;
        font-size: 2.2em;
        font-weight: 700;
        margin-bottom: 0.5em;
        letter-spacing: 1px;
        text-shadow: 0 2px 8px #e0e0e0;
    }
    .section-title {
        color: #1976d2;
        font-size: 1.25em;
        font-weight: 600;
        margin-top: 1.2em;
        margin-bottom: 0.5em;
        letter-spacing: 0.5px;
    }
    .info-badge {
        display: inline-block;
        background: #e3f2fd;
        border-radius: 8px;
        padding: 0.3em 0.8em;
        margin-right: 0.5em;
        margin-bottom: 0.3em;
        color: #1976d2;
        font-size: 1em;
    }
    .symptom-list, .cause-list, .treatment-list {
        margin-left: 1em;
        margin-bottom: 0.5em;
    }
    </style>
""", unsafe_allow_html=True)


st.markdown("""
    <div style='text-align: center; margin-top: 1em;'>
        <span style='font-size:2.5em;'>🌿</span>
        <h1 style='color: #1565c0; margin-bottom:0;'>Leaf Disease Detection</h1>
        <p style='color: #616161; font-size:1.15em;'>Upload a leaf image to detect diseases and get expert recommendations.</p>
    </div>
""", unsafe_allow_html=True)

api_url = "http://leaf-diseases-detect.vercel.app"

col1, col2 = st.columns([1, 2])
with col1:
    uploaded_file = st.file_uploader(
        "Tải ảnh", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Xem")

with col2:
    if uploaded_file is not None:
        if st.button("🔍 Phát hiện bệnh", use_container_width=True):
            with st.spinner("Đang phân tích và kết nối với API..."):
                try:
                    files = {
                        "file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    response = requests.post(
                        f"{api_url}/disease-detection-file", files=files)
                    if response.status_code == 200:
                        result = response.json()

                        # Check if it's an invalid image
                        if result.get("disease_type") == "invalid_image":
                            # Sau này xử lí, để kết quả vào 1 khung
                            # st.markdown("<div class='result-card'>",
                            #             unsafe_allow_html=True)
                            st.markdown(
                                "<div class='disease-title'>⚠️ Ảnh không hợp lệ</div>", unsafe_allow_html=True)
                            st.markdown(
<<<<<<< HEAD:streamlit_app.py
                                "<div style='color: #ff5722; font-size: 1.1em; margin-bottom: 1em;'>Vui lòng tải lại hình ảnh của lá cây.</div>", unsafe_allow_html=True)

=======
                                "<div style='color: #ff5722; font-size: 1.1em; margin-bottom: 1em;'>Please upload a clear image of a plant leaf for accurate disease detection.</div>", unsafe_allow_html=True)
                            st.markdown("</div>", unsafe_allow_html=True)
                            
>>>>>>> main:main.py
                            # Show the symptoms (which contain the error message)
                            if result.get("symptoms"):
                                st.markdown(
                                    "<div class='section-title'>Vấn đề</div>", unsafe_allow_html=True)
                                st.markdown("<ul class='symptom-list'>",
                                            unsafe_allow_html=True)
                                for symptom in result.get("symptoms", []):
                                    st.markdown(
                                        f"<li>{symptom}</li>", unsafe_allow_html=True)
                                st.markdown("</ul>", unsafe_allow_html=True)

                            # Show treatment recommendations
                            if result.get("treatment"):
                                st.markdown(
                                    "<div class='section-title'>Lời khuyên</div>", unsafe_allow_html=True)
                                st.markdown("<ul class='treatment-list'>",
                                            unsafe_allow_html=True)
                                for treat in result.get("treatment", []):
                                    st.markdown(
                                        f"<li>{treat}</li>", unsafe_allow_html=True)
                                st.markdown("</ul>", unsafe_allow_html=True)

                            st.markdown("</div>", unsafe_allow_html=True)

                        elif result.get("disease_detected"):
                            st.markdown("<div class='result-card'>",
                                        unsafe_allow_html=True)
                            st.markdown(
                                f"<div class='disease-title'>🦠 {result.get('disease_name', 'N/A')}</div>", unsafe_allow_html=True)
                            st.markdown(
                                f"<span class='info-badge'>Loại: {result.get('disease_type', 'N/A')}</span>", unsafe_allow_html=True)
                            st.markdown(
                                f"<span class='info-badge'>Mức độ: {result.get('severity', 'N/A')}</span>", unsafe_allow_html=True)
                            st.markdown(
                                f"<span class='info-badge'>Đáng tin cậy: {result.get('confidence', 'N/A')}%</span>", unsafe_allow_html=True)
                            st.markdown(
                                "<div class='section-title'>Triệu chứng</div>", unsafe_allow_html=True)
                            st.markdown("<ul class='symptom-list'>",
                                        unsafe_allow_html=True)
                            for symptom in result.get("symptoms", []):
                                st.markdown(
                                    f"<li>{symptom}</li>", unsafe_allow_html=True)
                            st.markdown("</ul>", unsafe_allow_html=True)
                            st.markdown(
                                "<div class='section-title'>Nguyên nhân</div>", unsafe_allow_html=True)
                            st.markdown("<ul class='cause-list'>",
                                        unsafe_allow_html=True)
                            for cause in result.get("possible_causes", []):
                                st.markdown(
                                    f"<li>{cause}</li>", unsafe_allow_html=True)
                            st.markdown("</ul>", unsafe_allow_html=True)
                            st.markdown(
                                "<div class='section-title'>Biện pháp xử lý</div>", unsafe_allow_html=True)
                            st.markdown("<ul class='treatment-list'>",
                                        unsafe_allow_html=True)
                            for treat in result.get("treatment", []):
                                st.markdown(
                                    f"<li>{treat}</li>", unsafe_allow_html=True)
                            st.markdown("</ul>", unsafe_allow_html=True)
                            st.markdown("</div>", unsafe_allow_html=True)
                        else:
                            # Healthy leaf case
                            st.markdown("<div class='result-card'>",
                                        unsafe_allow_html=True)
                            st.markdown(
                                "<div class='disease-title'>✅ Cây khoẻ mạnh</div>", unsafe_allow_html=True)
                            st.markdown(
                                "<div style='color: #4caf50; font-size: 1.1em; margin-bottom: 1em;'>Không phát hiện bệnh trên lá cây.</div>", unsafe_allow_html=True)
                            st.markdown(
                                f"<span class='info-badge'>Tình trạng: {result.get('disease_type', 'healthy')}</span>", unsafe_allow_html=True)
                            st.markdown(
                                f"<span class='info-badge'>Đáng tin cậy: {result.get('confidence', 'N/A')}%</span>", unsafe_allow_html=True)
                            st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.error(f"API Error: {response.status_code}")
                        st.write(response.text)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
