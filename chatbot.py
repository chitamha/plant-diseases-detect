"""
Chatbot Module for Leaf Disease Detection System
================================================

This module provides a conversational AI chatbot that can answer questions
about plant diseases, provide advice, and assist users with the leaf disease
detection system. All responses are in Vietnamese.

Features:
    - Answer questions about plant diseases
    - Provide treatment recommendations
    - Explain disease symptoms
    - Give farming advice
    - Context-aware conversation with chat history
"""

import os
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

from groq import Groq
from dotenv import load_dotenv


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ChatMessage:
    """
    Data class to represent a single chat message.
    
    Attributes:
        role (str): Role of the message sender ("user" or "assistant")
        content (str): Content of the message
    """
    role: str
    content: str


class PlantDiseaseChatbot:
    """
    Conversational AI Chatbot for Plant Disease Consultation.
    
    This chatbot uses Groq API with Llama models to provide expert advice
    on plant diseases, treatments, and general farming questions. All
    interactions are conducted in Vietnamese.
    
    The chatbot maintains conversation history to provide context-aware
    responses and can answer questions about:
    - Plant disease identification and symptoms
    - Treatment methods and recommendations
    - Disease prevention strategies
    - General plant care and farming advice
    
    Attributes:
        MODEL_NAME (str): The AI model used for chat
        DEFAULT_TEMPERATURE (float): Default temperature for response generation
        DEFAULT_MAX_TOKENS (int): Default max tokens for responses
        api_key (str): Groq API key for authentication
        client (Groq): Instance of the Groq API client
        chat_history (List[ChatMessage]): History of the conversation
    
    Example:
        >>> chatbot = PlantDiseaseChatbot()
        >>> response = chatbot.chat("Bệnh đốm lá nâu là gì?")
        >>> print(response)
    """
    
    MODEL_NAME = "llama-3.3-70b-versatile"
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_MAX_TOKENS = 1024
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Plant Disease Chatbot with API credentials.
        
        Sets up the Groq API client and validates the API key from parameter
        or environment variable. Initializes logging for tracking chat operations
        and creates an empty chat history.
        
        Args:
            api_key (Optional[str]): Groq API key. If None, will attempt to
                                     load from GROQ_API_KEY environment variable.
        
        Raises:
            ValueError: If no valid API key is found in parameters or environment.
        
        Note:
            Ensure your .env file contains GROQ_API_KEY or pass it directly.
        """
        load_dotenv()
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GROQ_API_KEY không được tìm thấy trong biến môi trường"
            )
        self.client = Groq(api_key=self.api_key)
        self.chat_history: List[ChatMessage] = []
        logger.info("Khởi tạo Plant Disease Chatbot")
    
    def _create_system_prompt(self) -> str:
        """
        Create the system prompt that defines the chatbot's personality and role.
        
        Returns:
            str: System prompt for the chatbot
        """
        return """BẠN LÀ CHUYÊN GIA TƯ VẤN BỆNH CÂY TRỒNG thân thiện và am hiểu sâu sắc về:
- Bệnh cây trồng (nấm, vi khuẩn, vi rút, sâu bệnh)
- Triệu chứng và cách nhận biết bệnh
- Phương pháp điều trị và phòng ngừa
- Chăm sóc cây trồng và kỹ thuật canh tác
- Dinh dưỡng và phân bón

NHIỆM VỤ CỦA BẠN:
✓ Trả lời câu hỏi của người dùng một cách rõ ràng, chính xác
✓ Cung cấp lời khuyên thiết thực, dễ áp dụng
✓ Giải thích bằng ngôn ngữ đơn giản, dễ hiểu
✓ Thân thiện, nhiệt tình như một người bạn đồng hành
✓ Hỏi lại nếu cần thêm thông tin để tư vấn tốt hơn

CÁCH TRẢ LỜI:
- Sử dụng TIẾNG VIỆT trong mọi câu trả lời
- Trả lời ngắn gọn nhưng đầy đủ thông tin
- Chia nhỏ thành các bước nếu câu trả lời dài
- Sử dụng emoji phù hợp để thân thiện hơn
- Đưa ra ví dụ cụ thể khi có thể

QUAN TRỌNG:
- Nếu không chắc chắn, hãy thừa nhận và đề xuất người dùng tham khảo thêm
- Không đưa ra lời khuyên có thể gây hại cho cây hoặc người dùng
- Khuyến khích người dùng sử dụng tính năng phát hiện bệnh bằng ảnh nếu cần chẩn đoán chính xác"""
    
    def chat(
        self,
        user_message: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Send a message to the chatbot and get a response.
        
        This method maintains the conversation history and provides
        context-aware responses based on previous messages in the chat.
        
        Args:
            user_message (str): The user's message/question
            temperature (Optional[float]): Temperature for response generation
            max_tokens (Optional[int]): Maximum tokens for the response
        
        Returns:
            str: The chatbot's response in Vietnamese
        
        Raises:
            ValueError: If user_message is empty
            Exception: If the API call fails
        
        Example:
            >>> chatbot = PlantDiseaseChatbot()
            >>> response = chatbot.chat("Cách chữa bệnh phấn trắng?")
            >>> print(response)
        """
        try:
            if not user_message or not user_message.strip():
                raise ValueError("Tin nhắn không thể để trống")
            
            logger.info(f"Nhận tin nhắn từ người dùng: {user_message[:50]}...")
            
            # Add user message to history
            self.chat_history.append(ChatMessage(
                role="user",
                content=user_message
            ))
            
            # Prepare messages for API
            messages = [
                {
                    "role": "system",
                    "content": self._create_system_prompt()
                }
            ]
            
            # Add chat history
            for msg in self.chat_history:
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            # Set parameters
            temperature = temperature or self.DEFAULT_TEMPERATURE
            max_tokens = max_tokens or self.DEFAULT_MAX_TOKENS
            
            # Make API request
            completion = self.client.chat.completions.create(
                model=self.MODEL_NAME,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=1,
                stream=False,
                stop=None,
            )
            
            # Extract response
            assistant_message = completion.choices[0].message.content
            
            # Add assistant response to history
            self.chat_history.append(ChatMessage(
                role="assistant",
                content=assistant_message
            ))
            
            logger.info("Chatbot đã trả lời thành công")
            return assistant_message
            
        except Exception as e:
            logger.error(f"Lỗi khi chat: {str(e)}")
            raise
    
    def clear_history(self):
        """
        Clear the conversation history.
        
        This resets the chatbot to start a fresh conversation without
        any context from previous messages.
        """
        self.chat_history = []
        logger.info("Đã xóa lịch sử chat")
    
    def get_history(self) -> List[Dict[str, str]]:
        """
        Get the conversation history.
        
        Returns:
            List[Dict[str, str]]: List of messages with role and content
        """
        return [
            {"role": msg.role, "content": msg.content}
            for msg in self.chat_history
        ]


def main():
    """Main execution function for testing the chatbot."""
    try:
        # Create chatbot instance
        chatbot = PlantDiseaseChatbot()
        print("✅ Plant Disease Chatbot đã sẵn sàng!")
        print("📝 Hỏi tôi bất cứ điều gì về bệnh cây trồng...\n")
        
        # Interactive chat loop for testing
        while True:
            user_input = input("Bạn: ")
            if user_input.lower() in ['exit', 'quit', 'thoát']:
                print("👋 Tạm biệt!")
                break
            
            if user_input.lower() == 'clear':
                chatbot.clear_history()
                print("🔄 Đã xóa lịch sử chat\n")
                continue
            
            try:
                response = chatbot.chat(user_input)
                print(f"\n🌿 Chuyên gia: {response}\n")
            except Exception as e:
                print(f"❌ Lỗi: {str(e)}\n")
    
    except Exception as e:
        print(f"Error: {str(e)}")
        import sys
        sys.exit(1)


if __name__ == "__main__":
    main()
