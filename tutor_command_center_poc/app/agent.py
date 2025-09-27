import os
import json
from datetime import datetime
from typing import Dict, Any, List
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool

from tools import assign_exercise, get_student_activity_log, grade_submission, add_note_to_report, create_custom_pathway, list_available_submissions

# Load environment variables
load_dotenv()


def configure_gemini():
    """Configure Gemini API with tools."""
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    
    # Define function declarations for Gemini
    assign_exercise_func = FunctionDeclaration(
        name="assign_exercise",
        description="Assign exercises to a student based on learning object title",
        parameters={
            "type": "object",
            "properties": {
                "student_name": {
                    "type": "string",
                    "description": "The name of the student to assign exercises to"
                },
                "learning_object_title": {
                    "type": "string",
                    "description": "The title of the learning object/topic"
                },
                "num_questions": {
                    "type": "integer",
                    "description": "Number of questions to assign"
                }
            },
            "required": ["student_name", "learning_object_title", "num_questions"]
        }
    )
    
    get_activity_log_func = FunctionDeclaration(
        name="get_student_activity_log",
        description="Get activity log for a specific student",
        parameters={
            "type": "object",
            "properties": {
                "student_name": {
                    "type": "string",
                    "description": "The name of the student"
                },
                "date_range": {
                    "type": "string",
                    "description": "Date range filter (e.g., 'today', 'this_week', etc.)"
                }
            },
            "required": ["student_name"]
        }
    )
    
    grade_submission_func = FunctionDeclaration(
        name="grade_submission",
        description="Grade a student submission and provide feedback",
        parameters={
            "type": "object",
            "properties": {
                "submission_id": {
                    "type": "string",
                    "description": "The ID of the submission to grade"
                },
                "score": {
                    "type": "number",
                    "description": "The score to assign (0-100)"
                },
                "feedback_text": {
                    "type": "string",
                    "description": "Detailed feedback text for the student"
                }
            },
            "required": ["submission_id", "score", "feedback_text"]
        }
    )
    
    add_note_func = FunctionDeclaration(
        name="add_note_to_report",
        description="Add a tutor note to student's progress report",
        parameters={
            "type": "object",
            "properties": {
                "student_name": {
                    "type": "string",
                    "description": "The name of the student"
                },
                "note_text": {
                    "type": "string",
                    "description": "The note text to add to the student's report"
                }
            },
            "required": ["student_name", "note_text"]
        }
    )
    
    create_pathway_func = FunctionDeclaration(
        name="create_custom_pathway",
        description="Create a custom learning pathway for a student with specific learning objects",
        parameters={
            "type": "object",
            "properties": {
                "student_name": {
                    "type": "string",
                    "description": "The name of the student"
                },
                "learning_object_titles": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of learning object titles to include in the pathway"
                }
            },
            "required": ["student_name", "learning_object_titles"]
        }
    )
    
    list_submissions_func = FunctionDeclaration(
        name="list_available_submissions",
        description="List all available submissions that can be graded",
        parameters={
            "type": "object",
            "properties": {},
            "required": []
        }
    )
    
    # Create tool with function declarations
    tool = Tool(function_declarations=[
        assign_exercise_func, 
        get_activity_log_func, 
        grade_submission_func, 
        add_note_func, 
        create_pathway_func,
        list_submissions_func
    ])
    
    # Initialize model with tools and system instruction
    system_instruction = """
    Bạn là ISY - trợ lý AI thông minh cho gia sư, chuyên hỗ trợ quản lý học sinh và hoạt động giảng dạy.

    NGUYÊN TẮC HOẠT ĐỘNG:
    1. **Thực hiện trước, báo cáo sau**: Luôn ưu tiên thực hiện yêu cầu của gia sư trước, sau đó báo cáo kết quả chi tiết.
    
    2. **Mapping thông minh chủ đề**: Khi gia sư nói chủ đề chung, hãy map sang chủ đề cụ thể:
       - "hình học" → dùng "tứ giác" (có sẵn trong hệ thống)
       - "đại số" → dùng "phương trình" (có sẵn trong hệ thống)
       - Luôn thử map trước khi báo lỗi không tìm thấy
    
    3. **Yêu cầu thông tin thiếu**: Chỉ hỏi lại khi THỰC SỰ thiếu thông tin cần thiết:
       - "Giao bài tập cho An" (thiếu chủ đề và số câu) → Hỏi lại
       - "Chấm bài" (thiếu submission ID) → Liệt kê bài nộp available
       - "Thêm ghi chú cho Bình: [nội dung cụ thể]" → THỰC HIỆN NGAY, không hỏi
    
    4. **Xác nhận hành động**: CHỈ xác nhận cho các trường hợp THỰC SỰ nguy hiểm:
       - Chấm điểm dưới 30 (có thể làm học sinh buồn)
       - Giao quá 15 bài tập cùng lúc (quá tải)
       - Xóa dữ liệu (không áp dụng trong hệ thống này)
       
       KHÔNG XÁC NHẬN cho:
       - Thêm ghi chú bình thường
       - Giao bài tập số lượng hợp lý (<15)
       - Tạo lộ trình học tập
       - Chấm điểm bình thường (30-100)
    
    5. **Giao tiếp thân thiện**: 
       - Xưng "em", gọi gia sư "thầy/cô"
       - Sử dụng emoji: 📚✅⚠️🎯
       - Báo cáo kết quả chi tiết sau khi thực hiện
    
    6. **Hỗ trợ proactive**: 
       - Gợi ý hành động tiếp theo
       - Cảnh báo nếu có vấn đề
       - Cung cấp thống kê hữu ích

    CÁC CÔNG CỤ AVAILABLE:
    - assign_exercise: Giao bài tập cho học sinh
    - get_student_activity_log: Xem hoạt động của học sinh  
    - grade_submission: Chấm điểm bài nộp
    - add_note_to_report: Thêm ghi chú vào báo cáo học sinh
    - create_custom_pathway: Tạo lộ trình học tập tùy chỉnh
    - list_available_submissions: Liệt kê bài nộp có thể chấm

    QUAN TRỌNG: Hãy THỰC HIỆN yêu cầu trước, sau đó báo cáo kết quả. Đừng hỏi xác nhận không cần thiết!
    """
    
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        tools=[tool],
        system_instruction=system_instruction
    )
    
    return model


def execute_function_call(function_name: str, args: Dict[str, Any]) -> str:
    """Execute the appropriate function based on function name and arguments."""
    if function_name == "assign_exercise":
        return assign_exercise(
            student_name=args.get("student_name"),
            learning_object_title=args.get("learning_object_title"),
            num_questions=args.get("num_questions")
        )
    elif function_name == "get_student_activity_log":
        return get_student_activity_log(
            student_name=args.get("student_name"),
            date_range=args.get("date_range", "today")
        )
    elif function_name == "grade_submission":
        return grade_submission(
            submission_id=args.get("submission_id"),
            score=args.get("score"),
            feedback_text=args.get("feedback_text")
        )
    elif function_name == "add_note_to_report":
        return add_note_to_report(
            student_name=args.get("student_name"),
            note_text=args.get("note_text")
        )
    elif function_name == "create_custom_pathway":
        return create_custom_pathway(
            student_name=args.get("student_name"),
            learning_object_titles=args.get("learning_object_titles", [])
        )
    elif function_name == "list_available_submissions":
        return list_available_submissions()
    else:
        return f"Unknown function: {function_name}"


def run_agent_flow(prompt: str) -> Dict[str, Any]:
    """
    Run the complete agent flow with function calling capability and detailed logging.
    
    Args:
        prompt: User's natural language command
        
    Returns:
        Dictionary containing final response and detailed logs
    """
    logs = []
    start_time = datetime.now()
    turn_count = 0  # Initialize turn_count early to avoid reference errors
    
    def add_log(step: str, status: str, message: str, details: Dict[str, Any] = None):
        """Add a log entry with timestamp."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "step": step,
            "status": status,  # "processing", "success", "error", "info"
            "message": message,
            "details": details or {}
        }
        logs.append(log_entry)
        return log_entry
    
    try:
        add_log("initialization", "processing", "🤖 Khởi tạo AI Agent với Gemini API...")
        
        model = configure_gemini()
        chat = model.start_chat()
        
        add_log("initialization", "success", "✅ Khởi tạo thành công Gemini model")
        add_log("prompt_analysis", "processing", f"📝 Phân tích lệnh: '{prompt}'")
        
        # Send initial prompt
        response = chat.send_message(prompt)
        add_log("prompt_analysis", "success", "✅ Đã gửi lệnh đến AI, đang chờ phản hồi...")
        
        max_turns = 10  # Prevent infinite loops
        
        # Handle function calling loop
        while response.candidates[0].content.parts and turn_count < max_turns:
            turn_count += 1
            add_log("processing", "info", f"🔄 Xử lý turn {turn_count}")
            
            # Check if we have any function calls in this turn
            function_calls = []
            text_parts = []
            
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'function_call') and part.function_call:
                    function_calls.append(part.function_call)
                elif hasattr(part, 'text') and part.text:
                    text_parts.append(part.text)
            
            # If we have function calls, execute them all
            if function_calls:
                add_log("function_detection", "success", f"🛠️ Phát hiện {len(function_calls)} function call(s)")
                
                function_responses = []
                
                for i, function_call in enumerate(function_calls):
                    function_name = function_call.name
                    function_args = {}
                    
                    # Extract function arguments - convert protobuf to native Python types
                    for key, value in function_call.args.items():
                        # Convert protobuf RepeatedComposite to native Python list
                        if hasattr(value, '__iter__') and not isinstance(value, (str, bytes)):
                            try:
                                # Handle list/array types from protobuf
                                function_args[key] = list(value)
                            except:
                                # Fallback to original value if conversion fails
                                function_args[key] = value
                        else:
                            # Handle scalar types
                            function_args[key] = value
                    
                    add_log("function_execution", "processing", 
                           f"⚙️ Thực thi function {i+1}/{len(function_calls)}: {function_name}",
                           {"function_name": function_name, "arguments": function_args})
                    
                    # Execute the function
                    function_result = execute_function_call(function_name, function_args)
                    
                    add_log("function_execution", "success", 
                           f"✅ Hoàn thành {function_name}",
                           {"result_preview": function_result[:100] + "..." if len(function_result) > 100 else function_result})
                    
                    # Add to response list
                    function_responses.append({
                        "function_response": {
                            "name": function_name,
                            "response": {"result": function_result}
                        }
                    })
                
                add_log("function_results", "processing", "📤 Gửi kết quả functions trở lại AI...")
                
                # Send all function results back to model
                response = chat.send_message(function_responses)
                
                add_log("function_results", "success", "✅ AI đã nhận kết quả và đang tổng hợp phản hồi...")
            
            # If we have text response and no function calls, return it
            elif text_parts:
                final_response = " ".join(text_parts)
                add_log("completion", "success", "🎉 Hoàn thành! Tạo phản hồi cuối cùng cho người dùng")
                
                end_time = datetime.now()
                processing_time = (end_time - start_time).total_seconds()
                
                return {
                    "response": final_response,
                    "logs": logs,
                    "processing_time": processing_time,
                    "turns_processed": turn_count,
                    "status": "success"
                }
            
            else:
                add_log("processing", "info", "⏸️ Không có function call hoặc text response, thoát vòng lặp")
                break
        
        # If we get here, try to extract any available text response
        if response.candidates[0].content.parts:
            final_parts = []
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'text') and part.text:
                    final_parts.append(part.text)
            
            if final_parts:
                final_response = " ".join(final_parts)
                add_log("completion", "success", "✅ Trích xuất được phản hồi cuối cùng")
                
                end_time = datetime.now()
                processing_time = (end_time - start_time).total_seconds()
                
                return {
                    "response": final_response,
                    "logs": logs,
                    "processing_time": processing_time,
                    "turns_processed": turn_count,
                    "status": "success"
                }
        
        add_log("completion", "error", "❌ Không thể tạo phản hồi cuối cùng")
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        return {
            "response": "Xin lỗi, tôi không thể xử lý yêu cầu của bạn.",
            "logs": logs,
            "processing_time": processing_time,
            "turns_processed": turn_count,
            "status": "error"
        }
        
    except Exception as e:
        add_log("error", "error", f"❌ Lỗi hệ thống: {str(e)}")
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        return {
            "response": f"Đã xảy ra lỗi: {str(e)}",
            "logs": logs,
            "processing_time": processing_time,
            "turns_processed": turn_count,
            "status": "error"
        }
        
        # If we get here, return the last text response if available
        if response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'text') and part.text:
                    return part.text
        
        return "Xin lỗi, tôi không thể xử lý yêu cầu của bạn."
        
    except Exception as e:
        return f"Đã xảy ra lỗi: {str(e)}"