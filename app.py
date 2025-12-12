from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
import os
import threading
from utils import convert_image_to_base64_and_test, test_with_base64_data
from chatbot import PlantDiseaseChatbot

# Định cấu hình ghi nhật ký
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="API Phát Hiện Bệnh Lá", version="1.0.0")

# Pydantic models for request validation
class ChatRequest(BaseModel):
    message: str
    temperature: float = 0.7
    max_tokens: int = 1024

class SetContextRequest(BaseModel):
    disease_analysis: dict

# Initialize chatbot (singleton pattern with thread safety)
chatbot_instance = None
chatbot_lock = threading.Lock()

def get_chatbot():
    """Get or create chatbot instance in a thread-safe manner"""
    global chatbot_instance
    if chatbot_instance is None:
        with chatbot_lock:
            # Double-check locking pattern
            if chatbot_instance is None:
                chatbot_instance = PlantDiseaseChatbot()
    return chatbot_instance

@app.post('/disease-detection-file')
async def disease_detection_file(file: UploadFile = File(...)):
    """
    Điểm cuối phát hiện bệnh trên ảnh lá bằng cách tải lên tệp ảnh trực tiếp.
    Chấp nhận nhiều phần/dữ liệu biểu mẫu với một tệp hình ảnh.
    """
    try:
        logger.info("Đã nhận được file hình ảnh để phát hiện bệnh")
        
        # Đọc tập tin đã tải lên vào bộ nhớ
        contents = await file.read()
        
    # Xử lý tập tin trực tiếp từ bộ nhớ
        result = convert_image_to_base64_and_test(contents)
        
    # Không cần dọn dẹp vì tệp không được lưu cục bộ
        
        if result is None:
            raise HTTPException(status_code=500, detail="Không thể xử lý tệp hình ảnh")
        logger.info("Phát hiện bệnh từ tệp đã hoàn tất thành công")
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi phát hiện bệnh (file): {str(e)}")
        raise HTTPException(status_code=500, detail=f"Lỗi máy chủ nội bộ: {str(e)}")


@app.get("/")
async def root():
    """Điểm cuối gốc cung cấp thông tin API"""
    return {
        "message": "API Phát Hiện Bệnh Lá",
        "version": "1.0.0",
        "endpoints": {
            "disease_detection_file": "/disease-detection-file (POST, file upload)",
            "chatbot": "/chatbot (POST, JSON with message field)",
            "chatbot_set_context": "/chatbot/set-context (POST, set disease analysis context)",
            "chatbot_clear_context": "/chatbot/clear-context (POST, clear disease context)",
            "chatbot_clear": "/chatbot/clear (POST, clear chat history)"
        }
    }


@app.post('/chatbot')
async def chatbot_endpoint(request: ChatRequest):
    """
    Điểm cuối chatbot để trò chuyện với AI về bệnh cây.
    Chấp nhận JSON với trường 'message'.
    """
    try:
        logger.info(f"Nhận tin nhắn chatbot: {request.message[:50]}...")
        
        # Get chatbot instance
        chatbot = get_chatbot()
        
        # Get response
        response = chatbot.chat(
            request.message,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        logger.info("Chatbot đã trả lời thành công")
        return JSONResponse(content={
            "response": response,
            "status": "success"
        })
        
    except ValueError as e:
        logger.error(f"Lỗi validation: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Lỗi chatbot: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Lỗi máy chủ nội bộ: {str(e)}")


@app.post('/chatbot/clear')
async def chatbot_clear():
    """
    Xóa lịch sử chat của chatbot.
    """
    try:
        logger.info("Yêu cầu xóa lịch sử chat")
        
        # Get chatbot instance and clear history
        chatbot = get_chatbot()
        chatbot.clear_history()
        
        logger.info("Đã xóa lịch sử chat thành công")
        return JSONResponse(content={
            "message": "Đã xóa lịch sử chat",
            "status": "success"
        })
        
    except Exception as e:
        logger.error(f"Lỗi khi xóa lịch sử: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Lỗi máy chủ nội bộ: {str(e)}")


@app.post('/chatbot/set-context')
async def chatbot_set_context(request: SetContextRequest):
    """
    Thiết lập context phân tích bệnh cho chatbot.
    Cho phép chatbot trả lời câu hỏi dựa trên kết quả phân tích cụ thể.
    """
    try:
        logger.info("Yêu cầu thiết lập context phân tích bệnh")
        
        # Get chatbot instance and set context
        chatbot = get_chatbot()
        chatbot.set_disease_context(request.disease_analysis)
        
        logger.info("Đã thiết lập context thành công")
        return JSONResponse(content={
            "message": "Đã thiết lập context phân tích bệnh",
            "status": "success"
        })
        
    except Exception as e:
        logger.error(f"Lỗi khi thiết lập context: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Lỗi máy chủ nội bộ: {str(e)}")


@app.post('/chatbot/clear-context')
async def chatbot_clear_context():
    """
    Xóa context phân tích bệnh của chatbot.
    """
    try:
        logger.info("Yêu cầu xóa context phân tích bệnh")
        
        # Get chatbot instance and clear context
        chatbot = get_chatbot()
        chatbot.clear_disease_context()
        
        logger.info("Đã xóa context thành công")
        return JSONResponse(content={
            "message": "Đã xóa context phân tích bệnh",
            "status": "success"
        })
        
    except Exception as e:
        logger.error(f"Lỗi khi xóa context: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Lỗi máy chủ nội bộ: {str(e)}")
