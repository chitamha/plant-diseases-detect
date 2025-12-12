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
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


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

class LeafDiseaseDetector:
    """
    Advanced Leaf Disease Detection System using AI Vision Analysis.

    Lớp này cung cấp khả năng phát hiện bệnh trên lá toàn diện bằng cách sử dụng API Groq với các mô hình Llama Vision.
    Nó có thể phân tích hình ảnh lá để xác định bệnh, đánh giá mức độ nghiêm trọng và đưa ra các khuyến nghị điều trị.
    Hệ thống cũng xác thực rằng hình ảnh được tải lên chứa lá cây thực tế và từ chối hình ảnh con người, động vật hoặc các đối tượng không phải thực vật khác.

    Hệ thống hỗ trợ hình ảnh được mã hóa base64 và trả về kết quả JSON có cấu trúc chứa thông tin bệnh, điểm tin cậy, triệu chứng, nguyên nhân và gợi ý điều trị.

    Tính năng:
        - Xác thực hình ảnh (đảm bảo hình ảnh được tải lên chứa lá cây)
        - Phát hiện nhiều loại bệnh (nấm, vi khuẩn, virus, sâu bệnh, thiếu dinh dưỡng)
        - Đánh giá mức độ nghiêm trọng (nhẹ, trung bình, nặng)
        - Tính điểm tin cậy (0-100%)
        - Xác định triệu chứng
        - Khuyến nghị điều trị
        - Xử lý lỗi mạnh mẽ và phân tích phản hồi
        - Phát hiện và từ chối loại hình ảnh không hợp lệ

    Thuộc tính:
        MODEL_NAME (str): Mô hình AI được sử dụng để phân tích
        DEFAULT_TEMPERATURE (float): Nhiệt độ mặc định để tạo phản hồi
        DEFAULT_MAX_TOKENS (int): Số lượng token tối đa mặc định cho phản hồi
        api_key (str): Khóa API Groq để xác thực
        client (Groq): Thể hiện của trình khách API Groq

    Ví dụ:
        >>> detector = LeafDiseaseDetector()
        >>> result = detector.analyze_leaf_image_base64(base64_image_data)
        >>> if result['disease_type'] == 'invalid_image':
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
        Phân tích dữ liệu hình ảnh được mã hóa base64 để tìm bệnh trên lá và trả về kết quả JSON.

        Đầu tiên xác nhận rằng hình ảnh có chứa một chiếc lá cây. Nếu hình ảnh hiển thị
        con người, động vật, đồ vật hoặc nội dung không phải thực vật khác, trả về một 
        phản hồi 'invalid_image'. Để có hình ảnh lá hợp lệ, hãy thực hiện phân tích bệnh.

        Tham số:
        base64_image (str): Dữ liệu hình ảnh được mã hóa Base64 (không có tiền tố data:image)
        temperature (float, optional): Nhiệt độ mô hình để tạo phản hồi
        max_tokens (int, optional): Số lượng token tối đa cho phản hồi

        Trả về:
            Dict: Kết quả phân tích dưới dạng từ điển (có thể tuần tự hóa JSON)
                 - Đối với hình ảnh không hợp lệ: disease_type sẽ là 'invalid_image'
                 - Đối với lá hợp lệ: kết quả phân tích bệnh chuẩn

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

            # Return as dictionary for JSON serialization
            return result.__dict__

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
