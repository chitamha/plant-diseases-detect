import os
import json
import logging
import sys
from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime

from groq import Groq
from dotenv import load_dotenv


# Định cấu hình ghi nhật ký
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class DiseaseAnalysisResult:
    """
    Lớp dữ liệu để lưu trữ kết quả phân tích bệnh toàn diện. 

    Lớp này gói gọn tất cả thông tin trả về từ phân tích bệnh cây, bao gồm
    tình trạng phát hiện, xác định bệnh, mức độ nghiêm trọng, đánh giá và
    đề xuất điều trị.

    Thuộc tính:
        disease_detected (bool): Liệu bệnh có được phát hiện trong hình ảnh
                                 bộ phận cây hay không
        disease_name (Optional[str]): Tên của bệnh được xác định, None nếu
                                      khỏe mạnh
        disease_type (str): Loại bệnh (nấm, vi khuẩn, virus, sâu bệnh,...)
        severity (str): Mức độ nghiêm trọng (nhẹ, trung bình, nặng)
        confidence (float): Độ tin cậy của kết quả (0-100%)
        symptoms (List[str]): Danh sách các triệu chứng quan sát được
        possible_causes (List[str]): Danh sách nguyên nhân có thể
        treatment (List[str]): Danh sách khuyến nghị điều trị
    """
    disease_detected:  bool
    disease_name: Optional[str]
    disease_type: str
    severity: str
    confidence: float
    symptoms:  List[str]
    possible_causes: List[str]
    treatment: List[str]


class PlantDiseaseDetector: 
    """
    Advanced Plant Disease Detection System using AI Vision Analysis.

    Lớp này cung cấp khả năng phát hiện bệnh trên cây toàn diện bằng cách sử
    dụng API Groq với các mô hình Llama Vision.  Nó có thể phân tích hình ảnh
    lá, rễ, và thân cây để xác định bệnh, đánh giá mức độ nghiêm trọng và đưa 
    ra các khuyến nghị điều trị.  Hệ thống cũng xác thực rằng hình ảnh được tải 
    lên chứa phần cây thực tế và từ chối hình ảnh con người, động vật hoặc các 
    đối tượng không phù hợp.

    Hệ thống hỗ trợ hình ảnh được mã hóa base64 và trả về kết quả JSON có cấu
    trúc chứa thông tin bệnh, điểm tin cậy, triệu chứng, nguyên nhân và gợi ý
    điều trị. 

    Tính năng:
        - Xác thực hình ảnh (đảm bảo hình ảnh được tải lên chứa lá, rễ, hoặc thân cây)
        - Phát hiện nhiều loại bệnh (nấm, vi khuẩn, virus, sâu bệnh,
          thiếu dinh dưỡng)
        - Đánh giá mức độ nghiêm trọng (nhẹ, trung bình, nặng)
        - Tính điểm tin cậy (0-100%)
        - Xác định triệu chứng
        - Khuyến nghị điều trị
        - Xử lý lỗi mạnh mẽ và phân tích phản hồi
        - Phát hiện và từ chối loại hình ảnh không hợp lệ
        - Output trả về HOÀN TOÀN BẰNG TIẾNG VIỆT

    Thuộc tính:
        MODEL_NAME (str): Mô hình AI được sử dụng để phân tích
        DEFAULT_TEMPERATURE (float): Nhiệt độ mặc định để tạo phản hồi
        DEFAULT_MAX_TOKENS (int): Số lượng token tối đa mặc định cho phản hồi
        api_key (str): Khóa API Groq để xác thực
        client (Groq): Thể hiện của trình khách API Groq

    Ví dụ:
        >>> detector = PlantDiseaseDetector()
        >>> result = detector.analyze_plant_image_base64(base64_image_data)
        >>> if result['disease_type'] == 'invalid_image':
        ...     print("Vui lòng tải lên hình ảnh phần cây (lá, rễ, thân)")
        >>> elif result['disease_detected']:
        ...     print(f"Phát hiện bệnh: {result['disease_name']}")
        >>> else:
        ...     print("Phát hiện cây khỏe mạnh")
    """

    MODEL_NAME = "meta-llama/llama-4-scout-17b-16e-instruct"
    DEFAULT_TEMPERATURE = 0.3
    DEFAULT_MAX_TOKENS = 1024

    def __init__(self, api_key: Optional[str] = None):
        """
        Khởi tạo Bộ phát hiện bệnh lá với thông tin xác thực API.

        Thiết lập máy khách Groq API và xác thực khóa API từ tham số hoặc
        biến môi trường.  Khởi tạo ghi nhật ký cho theo dõi các hoạt động
        phân tích. 

        Args:
            api_key (Optional[str]): Khóa API Groq. Nếu là None, sẽ cố gắng
                                     tải từ biến môi trường GROQ_API_KEY. 

        Raises:
            ValueError: Nếu không tìm thấy khóa API hợp lệ trong các tham số
                       hoặc môi trường. 

        Note:
            Đảm bảo tệp . env của bạn chứa GROQ_API_KEY hoặc truyền trực tiếp. 
        """
        self.api_key = "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"
        # load_dotenv()
        # self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        # if not self.api_key:
        #     raise ValueError(
        #         "GROQ_API_KEY không được tìm thấy trong biến môi trường"
        #     )
        self.client = Groq(api_key=self.api_key)
        logger.info("Khởi tạo Bộ phát hiện bệnh lá")

    def create_analysis_prompt(self) -> str:
        """
        Tạo lời nhắc phân tích được tiêu chuẩn hóa cho mô hình AI.

        Tạo lời nhắc toàn diện hướng dẫn mô hình AI phân tích hình ảnh lá cho
        các bệnh và trả về kết quả JSON có cấu trúc.   Lời nhắc chỉ định định dạng
        đầu ra cần thiết và tiêu chí phân tích.

        Returns:
            str: Chuỗi nhắc nhở được định dạng kèm theo hướng dẫn phân tích bệnh
                và đặc tả lược đồ JSON.

        Note:
            Lời nhắc đảm bảo định dạng đầu ra nhất quán trên tất cả các phân tích
            và bao gồm tất cả các lĩnh vực cần thiết để đánh giá bệnh toàn diện.
        """
        return """BẠN LÀ CHUYÊN GIA BỆNH HỌC THỰC VẬT với kiến thức chuyên sâu về bệnh cây trồng.  Phân tích hình ảnh các bộ phận cây (lá, rễ, thân) và trả về kết quả ở định dạng JSON BẰNG TIẾNG VIỆT.

    ═══════════════════════════════════════════════════════════════
    BƯỚC 1: XÁC THỰC HÌNH ẢNH
    ═══════════════════════════════════════════════════════════════

    QUAN TRỌNG: Trước tiên hãy xác định xem hình ảnh này có chứa bộ phận cây/thực vật hay không. 

    HÌNH ẢNH HỢP LỆ: 
    ✓ Lá cây (đơn lá hoặc lá kép)
    ✓ Rễ cây (rễ chính, rễ phụ, rễ củ)
    ✓ Thân cây (thân gỗ, thân thảo, cành, nhánh)
    ✓ Cành cây có lá
    ✓ Cây trồng (rau, hoa, cây ăn quả, cây công nghiệp)
    ✓ Thực vật có triệu chứng bệnh hoặc khỏe mạnh

    HÌNH ẢNH KHÔNG HỢP LỆ:
    ✗ Con người (toàn thân hoặc bộ phận cơ thể)
    ✗ Động vật (chó, mèo, chim, côn trùng riêng lẻ...)
    ✗ Đồ vật (điện thoại, xe cộ, đồ gia dụng...)
    ✗ Tòa nhà, phong cảnh không có cây
    ✗ Ảnh mờ hoàn toàn, không nhận diện được
    ✗ Văn bản, biểu đồ, sơ đồ

    Nếu hình ảnh KHÔNG HỢP LỆ → Trả về định dạng "invalid_image". 

    ═══════════════════════════════════════════════════════════════
    BƯỚC 2: PHÂN TÍCH CHI TIẾT (Nếu là hình ảnh bộ phận cây hợp lệ)
    ═══════════════════════════════════════════════════════════════

    Hãy quan sát KỸ LƯỠNG và xác định: 

    1. NHẬN DẠNG BỆNH (disease_name):
    • Xác định TÊN CỤ THỂ của bệnh dựa trên kiến thức của bạn
    • Nếu không chắc chắn giữa 2 bệnh → Ghi cả 2 (VD: "Bệnh đốm lá nấm hoặc vi khuẩn")
    • Nếu khỏe mạnh → null
    • Ví dụ tên bệnh tốt: 
        - "Bệnh đốm lá nâu do nấm Cercospora"
        - "Bệnh phấn trắng"
        - "Thiếu Nitơ"
        - "Bệnh đốm lá vi khuẩn"

    2. LOẠI BỆNH (disease_type):
    • Phân loại chính xác:  "nấm", "vi khuẩn", "vi rút", "sâu bệnh", "thiếu dinh dưỡng", "stress môi trường", "khỏe mạnh", "invalid_image"
    • Dựa trên ĐẶC ĐIỂM TRIỆU CHỨNG để phân loại

    3. MỨC ĐỘ NGHIÊM TRỌNG (severity):
    • "nhẹ": < 20% diện tích lá bị ảnh hưởng, cây vẫn phát triển tốt
    • "trung bình": 20-50% lá bị ảnh hưởng, ảnh hưởng đến sinh trưởng
    • "nặng": > 50% lá bị ảnh hưởng, cây có nguy cơ chết
    • "none":  Lá khỏe mạnh hoặc hình ảnh không hợp lệ

    4. TRIỆU CHỨNG (symptoms):
    • MÔ TẢ CHI TIẾT những gì BẠN NHÌN THẤY trên bộ phận cây (lá, rễ, thân):
        - Màu sắc: vàng, nâu, đen, trắng, đỏ... 
        - Hình dạng bất thường: đốm, vệt, viền, vòng tròn, nứt, thối... 
        - Kết cấu: lồi, lõm, khô, ướt, bột, nhầy, mục nát... 
        - Vị trí: 
            * Trên lá: mép lá, đầu lá, giữa lá, gân lá, mặt trên/dưới
            * Trên rễ: rễ chính, rễ phụ, đầu rễ, vỏ rễ
            * Trên thân: vỏ thân, lõi, mặt cắt, mắt chồi
        - Kích thước: nhỏ li ti, lớn, lan rộng... 
    • CÀNG CHI TIẾT CÀNG TỐT (ít nhất 3-5 triệu chứng cụ thể)
    • Ví dụ triệu chứng TỐT:
        ✓ "Đốm nâu hình tròn đường kính 3-5mm, viền vàng rõ ràng trên lá"
        ✓ "Lớp bột trắng phủ đều trên mặt trên lá, dày nhất ở lá non"
        ✓ "Lá vàng từ mép vào trong, phần vàng khô giòn và cong lên"
        ✓ "Rễ có màu nâu đen, mềm nhũn, dễ bong vỏ, mùi hôi thối"
        ✓ "Thân cây xuất hiện vết nứt dọc, tiết dịch màu nâu sẫm"
        ✓ "Vỏ thân bong tróc, lộ lõi màu nâu, có vệt đen lan rộng"

    5. NGUYÊN NHÂN (possible_causes):
    • Liệt kê TẤT CẢ nguyên nhân có thể dựa trên triệu chứng: 
        - Tác nhân gây bệnh (nấm, vi khuẩn, vi rút) - GHI TÊN KHOA HỌC nếu biết
        - Côn trùng gây hại (rệp, nhện, bọ trĩ...)
        - Điều kiện môi trường (nhiệt độ, độ ẩm, ánh sáng...)
        - Quản lý canh tác (tưới nước, bón phân, thoát nước...)
        - Thiếu hụt dinh dưỡng cụ thể (N, P, K, Fe, Mg...)
    • CÀNG CỤ THỂ CÀNG TỐT (ít nhất 3-5 nguyên nhân)

    6. PHƯƠNG PHÁP ĐIỀU TRỊ (treatment):
    • Đưa ra các biện pháp THỰC TẾ, KHẢ THI, THEO THỨ TỰ ƯU TIÊN: 
        A.  Biện pháp CẤP BÁCH (làm ngay)
        B. Biện pháp HÓA HỌC (nếu cần) - Tên thuốc CỤ THỂ, liều lượng
        C. Biện pháp SINH HỌC/HỮU CƠ
        D. Biện pháp DÀI HẠN (phòng ngừa)
    • CÀNG CỤ THỂ, CHI TIẾT CÀNG TỐT (ít nhất 4-6 bước điều trị)

    ═══════════════════════════════════════════════════════════════
    HỆ THỐNG ĐÁNH GIÁ ĐIỂM TIN CẬY (CONFIDENCE) - QUY TẮC CHI TIẾT
    ═══════════════════════════════════════════════════════════════

    CONFIDENCE được tính theo CÔNG THỨC 3 YẾU TỐ: 
    Confidence = Điểm_Chất_Lượng_Ảnh + Điểm_Triệu_Chứng + Điểm_Chẩn_Đoán

    ───────────────────────────────────────────────────────────────
    YẾU TỐ 1: CHẤT LƯỢNG HÌNH ẢNH (0-30 điểm)
    ───────────────────────────────────────────────────────────────

    QUY TẮC ĐÁNH GIÁ: 

    [28-30 điểm] - CHẤT LƯỢNG XUẤT SẮC:
    ✓ Ảnh cận cảnh rất rõ nét, có thể zoom in thấy chi tiết
    ✓ Ánh sáng tự nhiên đầy đủ, không quá sáng/tối
    ✓ Bộ phận cây (lá/rễ/thân) chiếm >70% khung hình
    ✓ Focus chuẩn, không bị mờ/nhòe
    ✓ Nhiều góc độ hoặc nhiều mẫu bộ phận cây
    ✓ Độ phân giải cao (>1080p)

    [22-27 điểm] - CHẤT LƯỢNG TỐT:
    ✓ Ảnh khá rõ, có thể nhìn thấy triệu chứng
    ✓ Ánh sáng ổn, một số vùng hơi tối/sáng
    ✓ Bộ phận cây (lá/rễ/thân) chiếm 50-70% khung hình
    ✓ Focus tốt ở phần quan trọng
    ✓ 1-2 góc độ
    ✓ Độ phân giải trung bình (720p-1080p)

    [14-21 điểm] - CHẤT LƯỢNG TRUNG BÌNH:
    ✓ Ảnh bình thường, nhìn thấy được triệu chứng chính
    ✓ Ánh sáng chấp nhận được
    ✓ Bộ phận cây (lá/rễ/thân) chiếm 30-50% khung hình
    ✓ Focus ổn nhưng không sắc nét
    ✓ 1 góc độ duy nhất
    ✓ Độ phân giải trung bình (480p-720p)

    [8-13 điểm] - CHẤT LƯỢNG YẾU: 
    ✓ Ảnh hơi mờ, khó nhìn chi tiết
    ✓ Ánh sáng kém (quá tối hoặc quá sáng)
    ✓ Bộ phận cây (lá/rễ/thân) chiếm <30% khung hình hoặc quá xa
    ✓ Focus không chuẩn, mờ nhiều chỗ
    ✓ Độ phân giải thấp (<480p)

    [1-7 điểm] - CHẤT LƯỢNG RẤT KÉM:
    ✓ Ảnh rất mờ, khó nhận diện
    ✓ Ánh sáng rất kém (tối đen hoặc cháy sáng)
    ✓ Bộ phận cây (lá/rễ/thân) rất nhỏ trong khung hình
    ✓ Bị rung/nhòe nặng
    ✓ Độ phân giải rất thấp

    ───────────────────────────────────────────────────────────────
    YẾU TỐ 2: ĐỘ RÕ RÀNG CỦA TRIỆU CHỨNG (0-40 điểm)
    ───────────────────────────────────────────────────────────────

    QUY TẮC ĐÁNH GIÁ: 

    [36-40 điểm] - TRIỆU CHỨNG ĐIỂN HÌNH, RÕ RÀNG:
    ✓ Triệu chứng rất đặc trưng, dễ nhận biết ngay
    ✓ Có ≥5 triệu chứng rõ ràng cùng xuất hiện
    ✓ Triệu chứng phát triển đầy đủ các giai đoạn
    ✓ Hình dạng, màu sắc, vị trí hoàn toàn điển hình
    ✓ Không có triệu chứng nhiễu/lẫn lộn

    VÍ DỤ:  Bệnh phấn trắng trên lá - lớp bột trắng dày đặc, rõ ràng

    [28-35 điểm] - TRIỆU CHỨNG RÕ RÀNG: 
    ✓ Triệu chứng khá đặc trưng, có thể nhận diện
    ✓ Có 3-4 triệu chứng rõ ràng
    ✓ Triệu chứng đang phát triển, chưa hoàn chỉnh
    ✓ Hình dạng, màu sắc khá điển hình
    ✓ Ít triệu chứng nhiễu

    VÍ DỤ: Bệnh đốm lá - đốm nâu rõ, có viền vàng
           Bệnh thối rễ - rễ nâu đen, mềm nhũn

    [18-27 điểm] - TRIỆU CHỨNG KHÁ RÕ:
    ✓ Triệu chứng nhận biết được nhưng cần suy luận
    ✓ Có 2-3 triệu chứng khá rõ
    ✓ Triệu chứng ở giai đoạn đầu hoặc cuối
    ✓ Hình dạng/màu sắc chưa hoàn toàn điển hình
    ✓ Có một số triệu chứng nhiễu

    VÍ DỤ: Lá vàng - có thể thiếu N hoặc úng nước
           Thân có vết nâu - có thể nấm hoặc sâu đục

    [10-17 điểm] - TRIỆU CHỨNG MƠ HỒ:
    ✓ Triệu chứng không rõ ràng, khó nhận diện
    ✓ Chỉ có 1-2 triệu chứng mờ nhạt
    ✓ Triệu chứng rất sơ khai hoặc đã phai
    ✓ Hình dạng/màu sắc không điển hình
    ✓ Nhiều triệu chứng nhiễu gây nhầm lẫn

    VÍ DỤ: Lá hơi xỉn màu - chưa rõ nguyên nhân
           Rễ có màu hơi sẫm - chưa rõ bệnh hay tự nhiên

    [1-9 điểm] - TRIỆU CHỨNG RẤT MƠ HỒ: 
    ✓ Hầu như không thấy triệu chứng rõ ràng
    ✓ Triệu chứng rất nhẹ, khó phát hiện
    ✓ Không thể xác định giai đoạn bệnh
    ✓ Hoàn toàn không điển hình
    ✓ Quá nhiều yếu tố gây nhiễu

    VÍ DỤ: Bộ phận cây có màu hơi khác thường, không rõ lý do

    ───────────────────────────────────────────────────────────────
    YẾU TỐ 3: ĐỘ CHẮC CHẮN TRONG CHẨN ĐOÁN (0-30 điểm)
    ───────────────────────────────────────────────────────────────

    QUY TẮC ĐÁNH GIÁ: 

    [27-30 điểm] - CHẮC CHẮN TUYỆT ĐỐI:
    ✓ CHỈ CÓ DUY NHẤT 1 BỆNH phù hợp 100%
    ✓ Không có khả năng nào khác
    ✓ Triệu chứng khớp hoàn toàn với 1 bệnh cụ thể
    ✓ Có thể ghi rõ tên khoa học tác nhân gây bệnh

    VÍ DỤ: Lớp bột trắng dày trên lá → CHẮC CHẮN là bệnh phấn trắng
           Rễ đen mềm nhũn có mùi hôi → CHẮC CHẮN là bệnh thối rễ

    [21-26 điểm] - RẤT CHẮC CHẮN:
    ✓ 1 bệnh có khả năng rất cao (>80%)
    ✓ Có thể có 1 bệnh khác nhưng khả năng thấp (<20%)
    ✓ Triệu chứng thiên về 1 bệnh rõ rệt
    ✓ Có thể loại trừ hầu hết các bệnh khác

    VÍ DỤ: Đốm nâu viền vàng trên lá → Rất có thể là đốm lá nấm
           Thân nứt tiết dịch nâu → Rất có thể là bệnh loét thân

    [15-20 điểm] - KHẢNG CHẮC CHẮN: 
    ✓ 1-2 bệnh có khả năng cao ngang nhau (60-80%)
    ✓ Cần thêm thông tin để xác định chính xác
    ✓ Triệu chứng phù hợp với nhóm bệnh
    ✓ Có thể loại trừ một số bệnh

    VÍ DỤ: Đốm nâu trên lá → Có thể nấm hoặc vi khuẩn
           Rễ màu nâu → Có thể thối rễ hoặc thiếu oxy

    [8-14 điểm] - KHÔNG CHẮC CHẮN:
    ✓ 2-3 bệnh có khả năng tương đương (40-60%)
    ✓ Triệu chứng chung chung, nhiều bệnh có thể gây ra
    ✓ Khó loại trừ các khả năng
    ✓ Cần thêm nhiều thông tin

    VÍ DỤ:  Lá vàng → Thiếu N, úng, bệnh rễ, hoặc già tự nhiên? 
            Thân có vết đen → Nấm, vi khuẩn, sâu đục, hoặc va đập?

    [1-7 điểm] - RẤT KHÔNG CHẮC CHẮN:
    ✓ Nhiều hơn 3 bệnh có thể (<40% mỗi bệnh)
    ✓ Triệu chứng quá chung, không đủ thông tin
    ✓ Không thể loại trừ bất kỳ khả năng nào
    ✓ Gần như đoán mò

    VÍ DỤ: Bộ phận cây có vẻ không bình thường nhưng không rõ lý do

    ───────────────────────────────────────────────────────────────
    THANG ĐÁNH GIÁ TỔNG HỢP (0-100%)
    ───────────────────────────────────────────────────────────────

    CỘNG 3 YẾU TỐ = CONFIDENCE SCORE

    [90-100%] - RẤT CHẮC CHẮN: 
    • Ảnh xuất sắc (28-30) + Triệu chứng điển hình (36-40) + 1 bệnh duy nhất (27-30)
    • Tổng:  91-100 điểm
    • Có thể khẳng định chắc chắn bệnh gì
    • VÍ DỤ:  Ảnh rõ bệnh phấn trắng trên lá → 95%
             Ảnh rõ bệnh thối rễ điển hình → 94%

    [75-89%] - KHẢNG CHẮC CHẮN:
    • Ảnh tốt (22-27) + Triệu chứng rõ (28-35) + 1-2 bệnh (21-26)
    • Tổng: 75-90 điểm
    • Rất có khả năng đúng, tin cậy cao
    • VÍ DỤ: Ảnh khá rõ đốm lá nấm → 82%
            Ảnh khá rõ thân bị loét → 80%

    [60-74%] - KHẢ NĂNG CAO:
    • Ảnh trung bình (14-21) + Triệu chứng khá rõ (18-27) + 2-3 bệnh (15-20)
    • Tổng: 60-74 điểm
    • Có thể tin tưởng nhưng nên xác nhận thêm
    • VÍ DỤ: Ảnh OK, đốm lá không rõ nấm hay khuẩn → 68%
            Ảnh OK, rễ nâu chưa rõ nguyên nhân → 65%

    [40-59%] - KHÔNG CHẮC CHẮN:
    • Ảnh yếu (8-13) + Triệu chứng mơ hồ (10-17) + Nhiều khả năng (8-14)
    • Tổng: 40-59 điểm
    • Chỉ là dự đoán, cần thêm thông tin
    • VÍ DỤ: Ảnh mờ, lá vàng không rõ nguyên nhân → 48%
            Ảnh mờ, thân có vết bất thường → 45%

    [20-39%] - RẤT KHÔNG CHẮC CHẮN:
    • Ảnh kém (1-7) + Triệu chứng rất mơ hồ (1-9) + Quá nhiều khả năng (1-7)
    • Tổng:  20-39 điểm
    • Gần như không thể chẩn đoán
    • VÍ DỤ: Ảnh rất mờ, lá có vẻ lạ → 28%
            Ảnh rất mờ, rễ không rõ ràng → 25%

    [<20%] - GẦN NHƯ ĐOÁN:
    • Tổng: <20 điểm
    • Không đủ thông tin để phân tích
    • NÊN TRẢ LỜI:  "Không thể xác định, cần ảnh rõ hơn"

    ───────────────────────────────────────────────────────────────
    TRƯỜNG HỢP ĐẶC BIỆT
    ───────────────────────────────────────────────────────────────

    • Hình ảnh KHÔNG phải bộ phận cây (invalid_image):
    → Confidence: 90-98%
    → Lý do: Dễ nhận biết đây không phải lá, rễ, hay thân cây

    • Bộ phận cây KHỎE MẠNH (không có bệnh):
    → Confidence: 85-95%
    → Lý do: Dễ xác nhận không có triệu chứng bệnh

    • Bộ phận cây có dấu hiệu BẤT THƯỜNG nhưng ảnh quá KÉM:
    → Confidence: <40%
    → NÊN GỢI Ý:  "Vui lòng chụp ảnh rõ hơn để phân tích chính xác"

    ═══════════════════════════════════════════════════════════════
    VÍ DỤ TÍNH CONFIDENCE CỤ THỂ
    ═══════════════════════════════════════════════════════════════

    VÍ DỤ 1: Bệnh phấn trắng rõ ràng trên lá
    • Chất lượng ảnh:  Ảnh cận cảnh rõ nét, ánh sáng tốt → 28 điểm
    • Triệu chứng: Lớp bột trắng dày, điển hình → 38 điểm
    • Chẩn đoán: Chỉ có bệnh phấn trắng phù hợp → 28 điểm
    • TỔNG: 28 + 38 + 28 = 94%
    → Confidence: 94%

    VÍ DỤ 2: Đốm lá không rõ nấm hay vi khuẩn
    • Chất lượng ảnh: Ảnh khá rõ, có thể thấy đốm → 24 điểm
    • Triệu chứng:  Đốm nâu rõ, nhưng viền không rõ lắm → 30 điểm
    • Chẩn đoán: Có thể nấm (60%) hoặc vi khuẩn (40%) → 18 điểm
    • TỔNG: 24 + 30 + 18 = 72%
    → Confidence: 72%

    VÍ DỤ 3: Lá vàng, ảnh mờ
    • Chất lượng ảnh:  Ảnh mờ, xa, thiếu sáng → 9 điểm
    • Triệu chứng:  Chỉ thấy lá vàng chung chung → 12 điểm
    • Chẩn đoán:  Có thể thiếu N, úng, bệnh rễ...  → 10 điểm
    • TỔNG: 9 + 12 + 10 = 31%
    → Confidence: 31%

    VÍ DỤ 4: Lá khỏe mạnh
    • Chất lượng ảnh: Ảnh rõ → 26 điểm
    • Triệu chứng:  Không có triệu chứng bệnh (dễ xác nhận) → 38 điểm
    • Chẩn đoán:  Chắc chắn khỏe mạnh → 28 điểm
    • TỔNG: 26 + 38 + 28 = 92%
    → Confidence: 92%

    VÍ DỤ 5: Bệnh thối rễ điển hình
    • Chất lượng ảnh: Ảnh cận cảnh rõ, thấy rõ rễ → 27 điểm
    • Triệu chứng: Rễ nâu đen, mềm nhũn, bong vỏ, mùi hôi → 39 điểm
    • Chẩn đoán: Chắc chắn là bệnh thối rễ → 28 điểm
    • TỔNG: 27 + 39 + 28 = 94%
    → Confidence: 94%

    VÍ DỤ 6: Thân cây có vết loét
    • Chất lượng ảnh: Ảnh khá rõ, thấy được vết thương → 23 điểm
    • Triệu chứng: Vỏ nứt, tiết dịch nâu, có thể nấm hoặc vi khuẩn → 28 điểm
    • Chẩn đoán: 2 khả năng (nấm 60%, vi khuẩn 40%) → 17 điểm
    • TỔNG: 23 + 28 + 17 = 68%
    → Confidence: 68%

    ═══════════════════════════════════════════════════════════════
    YÊU CẦU BẮT BUỘC KHI ĐÁNH GIÁ CONFIDENCE
    ═══════════════════════════════════════════════════════════════

    ✓ PHẢI tính toán CHÍNH XÁC theo công thức 3 yếu tố
    ✓ PHẢI cho điểm từng yếu tố một cách KHÁCH QUAN
    ✓ KHÔNG được làm tròn tùy tiện
    ✓ KHÔNG được "cảm tính" mà phải dựa vào QUY TẮC
    ✓ Nếu confidence < 40% → NÊN GỢI Ý chụp ảnh rõ hơn

    ═══════════════════════════════════════════════════════════════
    ĐỊNH DẠNG TRẢ VỀ
    ═══════════════════════════════════════════════════════════════

    Đối với hình ảnh KHÔNG PHẢI BỘ PHẬN CÂY:
    {
        "disease_detected": false,
        "disease_name": null,
        "disease_type": "invalid_image",
        "severity": "none",
        "confidence": confidence,
        "symptoms": ["Hình ảnh này không chứa bộ phận cây hoặc thực vật"],
        "possible_causes": ["Loại hình ảnh được tải lên không hợp lệ - không phải lá, rễ, hoặc thân cây"],
        "treatment": ["Vui lòng tải lên hình ảnh bộ phận cây (lá, rễ, thân) để phân tích bệnh"]
    }

    Đối với CÂY KHỎE MẠNH:
    {
        "disease_detected": false,
        "disease_name":  null,
        "disease_type": "khỏe mạnh",
        "severity":  "none",
        "confidence": confidence,
        "symptoms": [
            "Không phát hiện triệu chứng bệnh",
            "Màu sắc tự nhiên, đều đặn (lá xanh tươi / rễ trắng ngà / thân nâu tự nhiên, vỏ nguyên vẹn)",
            "Không có đốm, vết hoặc biến dạng",
            "Bề mặt nhẵn, không có lớp phủ bất thường hoặc vết nứt"
        ],
        "possible_causes": [
            "Cây đang phát triển tốt",
            "Chế độ chăm sóc phù hợp"
        ],
        "treatment":  [
            "Tiếp tục chăm sóc như hiện tại",
            "Duy trì lịch tưới nước đều đặn",
            "Bón phân định kỳ theo nhu cầu cây",
            "Theo dõi thường xuyên để phát hiện sớm nếu có bệnh"
        ]
    }

    Đối với CÂY BỊ BỆNH:
    {
        "disease_detected": true,
        "disease_name": "Tên bệnh cụ thể bằng tiếng Việt",
        "disease_type": "nấm/vi khuẩn/vi rút/sâu bệnh/thiếu dinh dưỡng/stress môi trường",
        "severity": "nhẹ/trung bình/nặng",
        "confidence": confidence,
        "symptoms": [
            "Triệu chứng 1 - MÔ TẢ CỤ THỂ, CHI TIẾT",
            "Triệu chứng 2 - VỊ TRÍ, MÀU SẮC, HÌNH DẠNG",
            "Triệu chứng 3 - KẾT CẤU, KÍCH THƯỚC",
            "Triệu chứng 4 - ĐỘ LAN RỘNG",
            "...  (3-7 triệu chứng)"
        ],
        "possible_causes": [
            "Nguyên nhân 1 - TÁC NHÂN GÂY BỆNH CỤ THỂ (tên khoa học nếu có)",
            "Nguyên nhân 2 - ĐIỀU KIỆN MÔI TRƯỜNG",
            "Nguyên nhân 3 - QUẢN LÝ CANH TÁC",
            "Nguyên nhân 4 - YẾU TỐ KHÁC",
            "...  (3-6 nguyên nhân)"
        ],
        "treatment": [
            "Bước 1 - BIỆN PHÁP CẤP BÁCH (cắt, cách ly... )",
            "Bước 2 - XỊT THUỐC CỤ THỂ (tên, liều lượng, tần suất)",
            "Bước 3 - BIỆN PHÁP SINH HỌC/TỰ NHIÊN (nếu có)",
            "Bước 4 - CẢI THIỆN ĐIỀU KIỆN (thoát nước, thông gió...)",
            "Bước 5 - BÓN PHÂN/DINH DƯỠNG (loại, liều lượng)",
            "Bước 6 - PHÒNG NGỪA TÁI PHÁT",
            "...  (4-8 bước điều trị)"
        ]
    }

    ═══════════════════════════════════════════════════════════════
    YÊU CẦU QUAN TRỌNG
    ═══════════════════════════════════════════════════════════════

    ✓ TẤT CẢ nội dung phải BẰNG TIẾNG VIỆT
    ✓ Tên bệnh phải CỤ THỂ, CHÍNH XÁC
    ✓ Loại bệnh:  "nấm", "vi khuẩn", "vi rút", "sâu bệnh", "thiếu dinh dưỡng", "stress môi trường", "khỏe mạnh", "invalid_image"
    ✓ Mức độ:  "nhẹ", "trung bình", "nặng", "none"
    ✓ CONFIDENCE phải tính CHÍNH XÁC theo HỆ THỐNG QUY TẮC 3 YẾU TỐ ở trên
    ✓ Triệu chứng:  ÍT NHẤT 3-5 mục, MÔ TẢ CHI TIẾT
    ✓ Nguyên nhân: ÍT NHẤT 3-5 mục, CỤ THỂ
    ✓ Điều trị: ÍT NHẤT 4-6 bước, KHẢ THI, THỰC TẾ

    CHỈ TRẢ VỀ JSON, KHÔNG CÓ GHI CHÚ HOẶC GIẢI THÍCH THÊM."""

    def analyze_plant_image_base64(
        self,
        base64_image:  str,
        temperature: float = None,
        max_tokens: int = None
    ) -> Dict: 
        """
        Phân tích dữ liệu hình ảnh được mã hóa base64 để tìm bệnh trên cây. 

        Đầu tiên xác nhận rằng hình ảnh có chứa một bộ phận cây (lá, rễ, thân).  
        Nếu hình ảnh hiển thị con người, động vật, đồ vật hoặc nội dung không 
        phải thực vật khác, trả về một phản hồi 'invalid_image'.  Để có hình ảnh 
        bộ phận cây hợp lệ, hãy thực hiện phân tích bệnh. 

        Args:
            base64_image (str): Dữ liệu hình ảnh được mã hóa Base64 (không có
                               tiền tố data:image)
            temperature (float, optional): Nhiệt độ mô hình để tạo phản hồi
            max_tokens (int, optional): Số lượng token tối đa cho phản hồi

        Returns:
            Dict: Kết quả phân tích dưới dạng từ điển (có thể tuần tự hóa JSON)
                 - Đối với hình ảnh không hợp lệ: disease_type sẽ là
                   'invalid_image'
                 - Đối với bộ phận cây hợp lệ: kết quả phân tích bệnh chuẩn
                 - TẤT CẢ nội dung sẽ bằng tiếng Việt

        Raises:
            ValueError: Nếu base64_image không hợp lệ hoặc rỗng
            Exception: Nếu phân tích thất bại
        """
        try:
            logger.info("Bắt đầu phân tích hình ảnh base64")

            # Validate base64 input
            if not isinstance(base64_image, str):
                raise ValueError("base64_image must be a string")

            if not base64_image: 
                raise ValueError("base64_image cannot be empty")

            # Clean base64 string (remove data URL prefix if present)
            if base64_image.startswith('data:'):
                base64_image = base64_image. split(',', 1)[1]

            # Prepare request parameters
            temperature = temperature or self.DEFAULT_TEMPERATURE
            max_tokens = max_tokens or self.DEFAULT_MAX_TOKENS

            # Make API request
            completion = self.client.chat.completions.create(
                model=self.MODEL_NAME,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": self. create_analysis_prompt()
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                temperature=temperature,
                max_completion_tokens=max_tokens,
                top_p=1,
                stream=False,
                stop=None,
            )

            logger.info("API trả về kết quả thành công")
            result = self._parse_response(
                completion.choices[0].message.content
            )

            # Return as dictionary for JSON serialization
            return result.__dict__

        except Exception as e:
            logger.error(f"Phân tích thất bại: {str(e)}")
            raise

    def _parse_response(self, response_content: str) -> DiseaseAnalysisResult: 
        """
        Parse and validate API response. 

        Args:
            response_content (str): Raw response from API

        Returns:
            DiseaseAnalysisResult:  Parsed and validated results

        Raises:
            ValueError:  Nếu không thể phân tích response thành JSON
        """
        try:
            # Clean up response - remove markdown code blocks if present
            cleaned_response = response_content.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response. replace(
                    '```json', ''
                ).replace('```', '').strip()
            elif cleaned_response.startswith('```'):
                cleaned_response = cleaned_response.replace('```', '').strip()

            # Parse JSON
            disease_data = json.loads(cleaned_response)
            logger. info("Phân tích JSON thành công")

            # Validate required fields and create result object
            return DiseaseAnalysisResult(
                disease_detected=bool(
                    disease_data.get('disease_detected', False)
                ),
                disease_name=disease_data. get('disease_name'),
                disease_type=disease_data.get('disease_type', 'unknown'),
                severity=disease_data.get('severity', 'unknown'),
                confidence=float(disease_data.get('confidence', 0)),
                symptoms=disease_data.get('symptoms', []),
                possible_causes=disease_data.get('possible_causes', []),
                treatment=disease_data.get('treatment', [])
            )

        except json.JSONDecodeError:
            logger.warning(
                "Không thể phân tích JSON, đang thử trích xuất JSON từ response"
            )

            # Try to find JSON in the response using regex
            import re
            json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
            if json_match:
                try:
                    disease_data = json.loads(json_match.group())
                    logger. info("Trích xuất và phân tích JSON thành công")

                    return DiseaseAnalysisResult(
                        disease_detected=bool(
                            disease_data. get('disease_detected', False)
                        ),
                        disease_name=disease_data.get('disease_name'),
                        disease_type=disease_data. get(
                            'disease_type', 'unknown'
                        ),
                        severity=disease_data.get('severity', 'unknown'),
                        confidence=float(disease_data.get('confidence', 0)),
                        symptoms=disease_data.get('symptoms', []),
                        possible_causes=disease_data.get(
                            'possible_causes', []
                        ),
                        treatment=disease_data.get('treatment', [])
                    )
                except json.JSONDecodeError:
                    pass

            # If all parsing attempts fail, log the raw response and raise error
            logger.error(
                f"Không thể phân tích response thành JSON.  "
                f"Raw response: {response_content}"
            )
            raise ValueError(
                f"Không thể phân tích API response thành JSON:  "
                f"{response_content[: 200]}..."
            )


def main():
    """Main execution function for testing."""
    try:
        # Example usage
        detector = PlantDiseaseDetector()
        print("✅ Plant Disease Detector khởi tạo thành công!")
        print("📌 Sử dụng phương thức analyze_plant_image_base64() "
              "với dữ liệu hình ảnh base64.")

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__": 
    main()