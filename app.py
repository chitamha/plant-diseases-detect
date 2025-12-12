from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
import logging
import os
from utils import convert_image_to_base64_and_test, test_with_base64_data

# Định cấu hình ghi nhật ký
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="API Phát Hiện Bệnh Lá", version="1.0.0")

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
            "disease_detection_file": "/disease-detection-file (POST, file upload)"
        }
    }
