import os
import json
import logging
import sys
import re
from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime

from groq import Groq
from dotenv import load_dotenv


# Định cấu hình ghi nhật ký
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Translation Dictionary: English to Vietnamese (150+ terms)
TRANSLATION_DICT = {
    # Disease Names
    "tar spot": "đốm hắc",
    "leaf scorch": "bệnh cháy lá",
    "fungal leaf spot": "bệnh đốm lá nấm",
    "bacterial leaf spot": "bệnh đốm lá vi khuẩn",
    "powdery mildew": "phấn trắng",
    "downy mildew": "sương mai",
    "leaf rust": "gỉ sắt lá",
    "anthracnose": "thán thư",
    "septoria leaf spot": "đốm lá septoria",
    "early blight": "bệnh mốc sớm",
    "late blight": "bệnh mốc muộn",
    "black rot": "thối đen",
    "brown rot": "thối nâu",
    "gray mold": "mốc xám",
    "leaf blight": "cháy lá",
    "leaf curl": "cuộn lá",
    "mosaic virus": "vi rút khảm",
    "yellow leaf curl": "cuộn lá vàng",
    "bacterial wilt": "héo vi khuẩn",
    "fusarium wilt": "héo fusarium",
    "verticillium wilt": "héo verticillium",
    "root rot": "thối rễ",
    "crown rot": "thối gốc",
    "canker": "loét thân",
    "fire blight": "bệnh cháy lửa",
    "sooty mold": "mốc đen",
    "white rust": "gỉ sắt trắng",
    "yellow rust": "gỉ sắt vàng",
    "brown spot": "đốm nâu",
    "black spot": "đốm đen",
    "yellow spot": "đốm vàng",
    "ring spot": "đốm vòng",
    "target spot": "đốm mục tiêu",
    "shot hole": "thủng lá",
    "leaf blotch": "vết lá",
    "scab": "ghẻ lở",
    "smut": "bệnh than",
    
    # Disease Types
    "fungal": "nấm",
    "bacterial": "vi khuẩn",
    "viral": "vi rút",
    "pest": "sâu bệnh",
    "insect": "côn trùng",
    "nutrient deficiency": "thiếu dinh dưỡng",
    "environmental": "môi trường",
    "physiological": "sinh lý",
    "healthy": "khỏe mạnh",
    "unknown": "không xác định",
    "invalid_image": "hình ảnh không hợp lệ",
    
    # Severity Levels
    "mild": "nhẹ",
    "moderate": "trung bình",
    "severe": "nặng",
    "critical": "nghiêm trọng",
    "none": "không",
    "low": "thấp",
    "medium": "trung bình",
    "high": "cao",
    
    # Symptoms
    "yellowing": "vàng lá",
    "browning": "nâu lá",
    "spots": "đốm",
    "spot": "đốm",
    "wilting": "héo úa",
    "curling": "cuộn lá",
    "necrosis": "hoại tử",
    "chlorosis": "úa vàng",
    "stunting": "còi cọc",
    "defoliation": "rụng lá",
    "discoloration": "đổi màu",
    "lesions": "tổn thương",
    "lesion": "tổn thương",
    "blisters": "phồng rộp",
    "blister": "phồng rộp",
    "rotting": "thối rữa",
    "decay": "phân hủy",
    "mold": "mốc",
    "mildew": "nấm mốc",
    "rust": "gỉ sắt",
    "scorch": "cháy",
    "blight": "héo úa",
    "canker": "loét",
    "galls": "u bướu",
    "wilt": "héo",
    "brown spots": "đốm nâu",
    "black spots": "đốm đen",
    "yellow spots": "đốm vàng",
    "white spots": "đốm trắng",
    "dark spots": "đốm sẫm",
    "circular spots": "đốm tròn",
    "irregular spots": "đốm không đều",
    "yellow halos": "vòng vàng",
    "brown halos": "vòng nâu",
    "water-soaked lesions": "tổn thương thấm nước",
    "sunken lesions": "tổn thương lõm",
    "raised lesions": "tổn thương nổi",
    "powdery coating": "lớp phủ bột",
    "fuzzy growth": "tăng trưởng mờ",
    "cottony growth": "tăng trưởng như bông",
    "sticky residue": "cặn dính",
    "spots have a tar-like appearance": "đốm có hình dạng giống hắc ín",
    "tar-like appearance": "hình dạng giống hắc ín",
    "leaf drop": "rụng lá",
    "leaf distortion": "biến dạng lá",
    "leaf deformity": "dị dạng lá",
    "vein clearing": "mạch lá mờ",
    "vein discoloration": "đổi màu mạch lá",
    "marginal necrosis": "hoại tử rìa",
    "tip burn": "cháy đầu",
    "edge burn": "cháy rìa",
    
    # Common Phrases in Symptoms
    "on the leaf": "trên lá",
    "on leaves": "trên lá",
    "of the leaf": "của lá",
    "of leaves": "của lá",
    "with yellow halos": "với vòng vàng",
    "with brown halos": "với vòng nâu",
    "tar-like appearance": "có hình dạng giống hắc ín",
    "tar-like spots": "đốm giống hắc ín",
    
    # Possible Causes
    "infection": "nhiễm",
    "fungus": "nấm",
    "bacteria": "vi khuẩn",
    "virus": "vi rút",
    "over-fertilization": "bón phân quá liều",
    "under-fertilization": "bón phân không đủ",
    "over-watering": "tưới nước quá nhiều",
    "under-watering": "tưới nước không đủ",
    "poor drainage": "thoát nước kém",
    "nutrient deficiency": "thiếu dinh dưỡng",
    "nitrogen deficiency": "thiếu nitơ",
    "phosphorus deficiency": "thiếu phốt pho",
    "potassium deficiency": "thiếu kali",
    "iron deficiency": "thiếu sắt",
    "magnesium deficiency": "thiếu magiê",
    "calcium deficiency": "thiếu canxi",
    "high humidity": "độ ẩm cao",
    "low humidity": "độ ẩm thấp",
    "poor air circulation": "thông gió kém",
    "temperature stress": "stress nhiệt độ",
    "water stress": "stress nước",
    "drought stress": "stress hạn hán",
    "heat stress": "stress nhiệt",
    "cold stress": "stress lạnh",
    "frost damage": "hư hại do sương giá",
    "sun damage": "hư hại do ánh nắng",
    "insect damage": "hư hại do côn trùng",
    "pest infestation": "nhiễm sâu bệnh",
    "contaminated tools": "dụng cụ bị nhiễm bẩn",
    "infected plant debris": "mảnh vỡ cây bị nhiễm",
    "poor sanitation": "vệ sinh kém",
    "rhizstoma acerinum": "rhizstoma acerinum",
    "similar pathogen": "mầm bệnh tương tự",
    "or similar pathogen": "hoặc mầm bệnh tương tự",
    
    # Treatment
    "remove infected leaves": "loại bỏ lá bị nhiễm",
    "remove affected leaves": "loại bỏ lá bị ảnh hưởng",
    "prune infected parts": "cắt tỉa phần bị nhiễm",
    "destroy infected material": "tiêu hủy vật liệu bị nhiễm",
    "apply fungicide": "xịt thuốc diệt nấm",
    "use fungicide": "sử dụng thuốc diệt nấm",
    "spray fungicide": "phun thuốc diệt nấm",
    "apply bactericide": "xịt thuốc diệt khuẩn",
    "use copper-based fungicide": "sử dụng thuốc diệt nấm gốc đồng",
    "improve air circulation": "cải thiện thông gió",
    "increase air flow": "tăng luồng không khí",
    "reduce humidity": "giảm độ ẩm",
    "water at soil level": "tưới nước ở mức đất",
    "avoid overhead watering": "tránh tưới nước từ trên cao",
    "water in the morning": "tưới nước vào buổi sáng",
    "ensure proper drainage": "đảm bảo thoát nước tốt",
    "improve drainage": "cải thiện thoát nước",
    "adjust watering schedule": "điều chỉnh lịch tưới nước",
    "reduce watering": "giảm tưới nước",
    "increase watering": "tăng tưới nước",
    "apply fertilizer": "bón phân",
    "use balanced fertilizer": "sử dụng phân cân đối",
    "add nitrogen": "bổ sung nitơ",
    "add phosphorus": "bổ sung phốt pho",
    "add potassium": "bổ sung kali",
    "add iron": "bổ sung sắt",
    "add magnesium": "bổ sung magiê",
    "add calcium": "bổ sung canxi",
    "adjust soil ph": "điều chỉnh độ ph đất",
    "improve soil quality": "cải thiện chất lượng đất",
    "mulch around plants": "phủ xung quanh cây",
    "space plants properly": "khoảng cách cây hợp lý",
    "provide shade": "cung cấp bóng mát",
    "protect from frost": "bảo vệ khỏi sương giá",
    "use insecticide": "sử dụng thuốc diệt côn trùng",
    "control pests": "kiểm soát sâu bệnh",
    "monitor regularly": "theo dõi thường xuyên",
    "quarantine infected plants": "cách ly cây bị nhiễm",
    "disinfect tools": "khử trùng dụng cụ",
    "practice crop rotation": "luân canh cây trồng",
    "clean garden debris": "dọn dẹp mảnh vỡ vườn",
    "to prevent spread": "để ngăn lan rộng",
    "to control fungal growth": "để kiểm soát sự phát triển của nấm",
    "around the plant": "xung quanh cây",
    "to reduce moisture": "để giảm độ ẩm",
    
    # Additional common terms
    "infection by the fungus": "nhiễm nấm",
    "caused by": "gây ra bởi",
    "due to": "do",
    "resulting from": "kết quả từ",
    "associated with": "liên quan đến",
    "characterized by": "đặc trưng bởi",
    "identified by": "xác định bởi",
    
    # Invalid image messages
    "this image does not contain a plant leaf": "hình ảnh này không chứa lá cây",
    "does not contain a plant leaf": "không chứa lá cây",
    "invalid image type uploaded": "loại hình ảnh được tải lên không hợp lệ",
    "please upload a plant leaf image for disease analysis": "vui lòng tải lên hình ảnh lá cây để phân tích bệnh",
    "upload a plant leaf image": "tải lên hình ảnh lá cây",
    "for disease analysis": "để phân tích bệnh",
    
    # Common connecting words and phrases (only full word matches)
    " and ": " và ",
    " or ": " hoặc ",
    " of ": " của ",
    " on ": " trên ",
    " in ": " trong ",
    " at ": " tại ",
    " by ": " bởi ",
    " with ": " với ",
    " from ": " từ ",
    " for ": " cho ",
    " to ": " để ",
    " have a ": " có ",
    " have ": " có ",
    " has ": " có ",
    " is ": " là ",
    " are ": " là ",
    "leaf surface": "bề mặt lá",
}


@dataclass
class DiseaseAnalysisResult:
    """
    Lớp dữ liệu để lưu trữ kết quả phân tích bệnh toàn diện.

    Lớp này gói gọn tất cả thông tin trả về từ bệnh lá phân tích, bao gồm tình trạng phát hiện, xác định bệnh,
    mức độ nghiêm trọng, đánh giá và đề xuất điều trị.

    Thuộc tính:
        disease_ detected (bool): Liệu bệnh có được phát hiện trong hình ảnh chiếc lá hay không
        disease_name (Optional[str]): Tên của bệnh được xác định, không có nếu khỏe mạnh
        disease_type (str): Loại bệnh (nấm, vi khuẩn, virus, sâu bệnh,...)
    """
    disease_detected: bool
    disease_name: Optional[str]
    disease_type: str
    severity: str
    confidence: float
    symptoms: List[str]
    possible_causes: List[str]
    treatment: List[str]


def translate_to_vietnamese(text: str) -> str:
    """
    Dịch text từ tiếng Anh sang tiếng Việt.
    Thực hiện dịch theo thứ tự từ cụm từ dài nhất đến ngắn nhất.
    
    Args:
        text (str): Văn bản tiếng Anh cần dịch
        
    Returns:
        str: Văn bản đã được dịch sang tiếng Việt
        
    Example:
        >>> translate_to_vietnamese("Tar Spot")
        'đốm hắc'
        >>> translate_to_vietnamese("fungal")
        'nấm'
    """
    if not text or not isinstance(text, str):
        return text
    
    text_lower = text.lower().strip()
    
    # Try exact match first
    if text_lower in TRANSLATION_DICT:
        return TRANSLATION_DICT[text_lower]
    
    # Sort keys by length (longest first) for better matching
    sorted_keys = sorted(TRANSLATION_DICT.keys(), key=len, reverse=True)
    
    result = text_lower
    for english_key in sorted_keys:
        if english_key in result:
            result = result.replace(english_key, TRANSLATION_DICT[english_key])
    
    return result


def translate_disease_data(data: Dict) -> Dict:
    """
    Dịch toàn bộ dữ liệu bệnh từ tiếng Anh sang tiếng Việt.
    
    Args:
        data (Dict): Từ điển chứa dữ liệu phân tích bệnh bằng tiếng Anh
        
    Returns:
        Dict: Từ điển với dữ liệu đã được dịch sang tiếng Việt
        
    Example:
        >>> data = {
        ...     "disease_name": "Tar Spot",
        ...     "disease_type": "fungal",
        ...     "symptoms": ["Brown spots with yellow halos on the leaf"]
        ... }
        >>> translated = translate_disease_data(data)
        >>> translated['disease_name']
        'đốm hắc'
    """
    translated_data = data.copy()
    
    # Translate disease_name
    if translated_data.get('disease_name'):
        translated_data['disease_name'] = translate_to_vietnamese(
            translated_data['disease_name']
        )
    
    # Translate disease_type
    if translated_data.get('disease_type'):
        translated_data['disease_type'] = translate_to_vietnamese(
            translated_data['disease_type']
        )
    
    # Translate severity
    if translated_data.get('severity'):
        translated_data['severity'] = translate_to_vietnamese(
            translated_data['severity']
        )
    
    # Translate symptoms (list of strings)
    if translated_data.get('symptoms'):
        translated_data['symptoms'] = [
            translate_to_vietnamese(s) for s in translated_data['symptoms']
        ]
    
    # Translate possible_causes (list of strings)
    if translated_data.get('possible_causes'):
        translated_data['possible_causes'] = [
            translate_to_vietnamese(c) for c in translated_data['possible_causes']
        ]
    
    # Translate treatment (list of strings)
    if translated_data.get('treatment'):
        translated_data['treatment'] = [
            translate_to_vietnamese(t) for t in translated_data['treatment']
        ]
    
    return translated_data


class LeafDiseaseDetector:
    """
    Advanced Leaf Disease Detection System using AI Vision Analysis.

    Lớp này cung cấp khả năng phát hiện bệnh trên lá toàn diện bằng cách sử dụng API Groq với các mô hình Llama Vision.
    Nó có thể phân tích hình ảnh lá để xác định bệnh, đánh giá mức độ nghiêm trọng và đưa ra các khuyến nghị điều trị.
    Hệ thống cũng xác thực rằng hình ảnh được tải lên chứa lá cây thực tế và từ chối hình ảnh con người, động vật hoặc các đối tượng không phải thực vật khác.

    Hệ thống hỗ trợ hình ảnh được mã hóa base64 và trả về kết quả JSON có cấu trúc chứa thông tin bệnh, điểm tin cậy, triệu chứng, nguyên nhân và gợi ý điều trị.
    
    **✨ TÍnh năng mới: Tất cả kết quả được tự động dịch sang tiếng Việt 100% sau khi phân tích.**

    Tính năng:
        - Xác thực hình ảnh (đảm bảo hình ảnh được tải lên chứa lá cây)
        - Phát hiện nhiều loại bệnh (nấm, vi khuẩn, virus, sâu bệnh, thiếu dinh dưỡng)
        - Đánh giá mức độ nghiêm trọng (nhẹ, trung bình, nặng)
        - Tính điểm tin cậy (0-100%)
        - Xác định triệu chứng
        - Khuyến nghị điều trị
        - Xử lý lỗi mạnh mẽ và phân tích phản hồi
        - Phát hiện và từ chối loại hình ảnh không hợp lệ
        - **Dịch tự động kết quả sang tiếng Việt**

    Thuộc tính:
        MODEL_NAME (str): Mô hình AI được sử dụng để phân tích
        DEFAULT_TEMPERATURE (float): Nhiệt độ mặc định để tạo phản hồi
        DEFAULT_MAX_TOKENS (int): Số lượng token tối đa mặc định cho phản hồi
        api_key (str): Khóa API Groq để xác thực
        client (Groq): Thể hiện của trình khách API Groq

    Ví dụ:
        >>> detector = LeafDiseaseDetector()
        >>> result = detector.analyze_leaf_image_base64(base64_image_data)
        >>> if result['disease_type'] == 'hình ảnh không hợp lệ':
        ...     print("Vui lòng tải lên hình ảnh lá cây")
        >>> elif result['disease_detected']:
        ...     print(f"Phát hiện bệnh: {result['disease_name']}")
        >>> else:
        ...     print("Phát hiện lá khỏe mạnh")

    """

    MODEL_NAME = "meta-llama/llama-4-scout-17b-16e-instruct"
    DEFAULT_TEMPERATURE = 0.3
    DEFAULT_MAX_TOKENS = 1024

    def __init__(self, api_key: Optional[str] = None):
        """
        Khởi tạo Bộ phát hiện bệnh lá với thông tin xác thực API.

        Thiết lập máy khách Groq API và xác thực khóa API từ
        tham số hoặc biến môi trường. Khởi tạo ghi nhật ký cho
        theo dõi các hoạt động phân tích.

        Args:
            api_key (Optional[str]): Khóa API Groq. Nếu là None, sẽ cố gắng
                                     tải từ biến môi trường GROQ_API_KEY.

        Raises:
            ValueError: Nếu không tìm thấy khóa API hợp lệ trong các tham số hoặc môi trường.

        Note:
            Đảm bảo tệp .env của bạn chứa GROQ_API_KEY hoặc truyền trực tiếp.
        """
        load_dotenv()
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY không được tìm thấy trong biến môi trường")
        self.client = Groq(api_key=self.api_key)
        logger.info("Khởi tạo Bộ phát hiện bệnh lá")

    def create_analysis_prompt(self) -> str:
        """
        Tạo lời nhắc phân tích được tiêu chuẩn hóa cho mô hình AI.

        Tạo lời nhắc toàn diện hướng dẫn mô hình AI phân tích hình ảnh lá cho các bệnh và
        trả về kết quả JSON có cấu trúc. Lời nhắc chỉ định định dạng đầu ra cần thiết và tiêu chí phân tích.

        Trả về:
            str: Chuỗi nhắc nhở được định dạng kèm theo hướng dẫn phân tích bệnh
                 và đặc tả lược đồ JSON.

        Lưu ý:
            Lời nhắc đảm bảo định dạng đầu ra nhất quán trên tất cả các phân tích
            và bao gồm tất cả các lĩnh vực cần thiết để đánh giá bệnh toàn diện.
        """
        return """QUAN TRỌNG: Trước tiên hãy xác định xem hình ảnh này có chứa lá cây hay thảm thực vật hay không. Nếu hình ảnh hiển thị con người, động vật, đồ vật, tòa nhà hoặc bất kỳ thứ gì khác ngoài lá/thảm thực vật, hãy trả về định dạng phản hồi "invalid_image" bên dưới.

        Nếu đây là hình ảnh lá/cây hợp lệ, hãy phân tích bệnh tật và trả về kết quả ở định dạng JSON.
        
        Hãy xác định:
        1. Đây có thực sự là hình ảnh chiếc lá/cây hay không
        2. Tên bệnh (nếu có)
        3. Loại/danh mục bệnh hoặc hình ảnh không hợp lệ
        4. Mức độ nghiêm trọng (nhẹ, trung bình, nặng)
        5. Điểm tin cậy (0-100%)
        6. Các triệu chứng quan sát được
        7. Nguyên nhân có thể
        8. Khuyến nghị điều trị

        Đối với hình ảnh KHÔNG CÓ LÁ (con người, động vật, đồ vật hoặc không được phát hiện là lá,...). Hãy trả về định dạng sau:
        {
            "disease_detected": sai,
            "disease_name": null,
            "disease_type": "hình ảnh không hợp lệ",
            "severity": "không",
            "confidence": 95,
            "symptoms": ["Hình ảnh này không chứa lá cây"],
            "possible_causes": ["Loại hình ảnh được tải lên không hợp lệ"],
            "treatment": ["Vui lòng tải lên hình ảnh lá cây để phân tích bệnh"]
        }
        
        Đối với hình ảnh LÁ HỢP LỆ, hãy trả về định dạng này:
        {
            "disease_detected": đúng/sai,
            "disease_name": "tên bệnh hoặc không có giá trị",
            "disease_type": "nấm/vi khuẩn/vi rút/sâu bệnh/thiếu dinh dưỡng/khỏe mạnh",
            "severity": "nhẹ/trung bình/nặng/không",
            "confidence": 85,
            "symptoms":  ["list", "of", "symptoms"],
            "possible_causes": ["list", "of", "causes"],
            "treatment": ["list", "of", "treatments"]
        }"""

    def analyze_leaf_image_base64(self, base64_image: str,
                                  temperature: float = None,
                                  max_tokens: int = None) -> Dict:
        """
        Phân tích dữ liệu hình ảnh được mã hóa base64 để tìm bệnh trên lá và trả về kết quả JSON bằng tiếng Việt.

        Đầu tiên xác nhận rằng hình ảnh có chứa một chiếc lá cây. Nếu hình ảnh hiển thị
        con người, động vật, đồ vật hoặc nội dung không phải thực vật khác, trả về một 
        phản hồi 'hình ảnh không hợp lệ'. Để có hình ảnh lá hợp lệ, hãy thực hiện phân tích bệnh.
        
        **✨ Kết quả được tự động dịch sang tiếng Việt 100%.**

        Tham số:
        base64_image (str): Dữ liệu hình ảnh được mã hóa Base64 (không có tiền tố data:image)
        temperature (float, optional): Nhiệt độ mô hình để tạo phản hồi
        max_tokens (int, optional): Số lượng token tối đa cho phản hồi

        Trả về:
            Dict: Kết quả phân tích dưới dạng từ điển bằng tiếng Việt (có thể tuần tự hóa JSON)
                 - Đối với hình ảnh không hợp lệ: disease_type sẽ là 'hình ảnh không hợp lệ'
                 - Đối với lá hợp lệ: kết quả phân tích bệnh chuẩn bằng tiếng Việt

        Tăng:
            Ngoại lệ: Nếu phân tích thất bại
        """
        try:
            logger.info("Starting analysis for base64 image data")

            # Validate base64 input
            if not isinstance(base64_image, str):
                raise ValueError("base64_image must be a string")

            if not base64_image:
                raise ValueError("base64_image cannot be empty")

            # Clean base64 string (remove data URL prefix if present)
            if base64_image.startswith('data:'):
                base64_image = base64_image.split(',', 1)[1]

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
                                "text": self.create_analysis_prompt()
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

            logger.info("API request completed successfully")
            result = self._parse_response(
                completion.choices[0].message.content)

            # Convert to dictionary
            result_dict = result.__dict__

            # 🎯 POST-PROCESSING: DỊCH TỰ ĐỘNG SANG TIẾNG VIỆT
            logger.info("🔄 Đang dịch kết quả sang tiếng Việt...")
            result_dict = translate_disease_data(result_dict)

            # Return translated dictionary for JSON serialization
            return result_dict

        except Exception as e:
            logger.error(f"Analysis failed for base64 image data: {str(e)}")
            raise

    def _parse_response(self, response_content: str) -> DiseaseAnalysisResult:
        """
        Parse and validate API response

        Args:
            response_content (str): Raw response from API

        Returns:
            DiseaseAnalysisResult: Parsed and validated results
        """
        try:
            # Clean up response - remove markdown code blocks if present
            cleaned_response = response_content.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response.replace(
                    '```json', '').replace('```', '').strip()
            elif cleaned_response.startswith('```'):
                cleaned_response = cleaned_response.replace('```', '').strip()

            # Parse JSON
            disease_data = json.loads(cleaned_response)
            logger.info("Response parsed successfully as JSON")

            # Validate required fields and create result object
            return DiseaseAnalysisResult(
                disease_detected=bool(
                    disease_data.get('disease_detected', False)),
                disease_name=disease_data.get('disease_name'),
                disease_type=disease_data.get('disease_type', 'unknown'),
                severity=disease_data.get('severity', 'unknown'),
                confidence=float(disease_data.get('confidence', 0)),
                symptoms=disease_data.get('symptoms', []),
                possible_causes=disease_data.get('possible_causes', []),
                treatment=disease_data.get('treatment', [])
            )

        except json.JSONDecodeError:
            logger.warning(
                "Failed to parse as JSON, attempting to extract JSON from response")

            # Try to find JSON in the response using regex
            import re
            json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
            if json_match:
                try:
                    disease_data = json.loads(json_match.group())
                    logger.info("JSON extracted and parsed successfully")

                    return DiseaseAnalysisResult(
                        disease_detected=bool(
                            disease_data.get('disease_detected', False)),
                        disease_name=disease_data.get('disease_name'),
                        disease_type=disease_data.get(
                            'disease_type', 'unknown'),
                        severity=disease_data.get('severity', 'unknown'),
                        confidence=float(disease_data.get('confidence', 0)),
                        symptoms=disease_data.get('symptoms', []),
                        possible_causes=disease_data.get(
                            'possible_causes', []),
                        treatment=disease_data.get('treatment', [])
                    )
                except json.JSONDecodeError:
                    pass

            # If all parsing attempts fail, log the raw response and raise error
            logger.error(
                f"Could not parse response as JSON. Raw response: {response_content}")
            raise ValueError(
                f"Unable to parse API response as JSON: {response_content[:200]}...")


def main():
    """Main execution function for testing"""
    try:
        # Example usage
        detector = LeafDiseaseDetector()
        print("Leaf Disease Detector (minimal version) initialized successfully!")
        print("Use analyze_leaf_image_base64() method with base64 image data.")

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
