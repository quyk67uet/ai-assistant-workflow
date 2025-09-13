import streamlit as st
import requests
import json
from typing import List, Dict

# Configuration
API_BASE_URL = "http://127.0.0.1:8000"

# Page configuration
st.set_page_config(
    page_title="ISY Tutor Command Center",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main app styling */
    .main {
        padding-top: 1rem;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    
    /* Success message styling */
    .element-container .stSuccess {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.375rem;
        padding: 0.75rem;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "api_available" not in st.session_state:
        st.session_state.api_available = check_api_health()


def check_api_health() -> bool:
    """Check if the FastAPI backend is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def send_command_to_api(prompt: str) -> Dict:
    """Send command to the FastAPI backend and return the response."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/tutor-command",
            json={"prompt": prompt},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "response": f"Lỗi API: {response.status_code} - {response.text}",
                "logs": [],
                "processing_time": 0,
                "turns_processed": 0,
                "status": "error"
            }
            
    except requests.exceptions.Timeout:
        return {
            "response": "Yêu cầu hết thời gian chờ. Vui lòng thử lại.",
            "logs": [],
            "processing_time": 0,
            "turns_processed": 0,
            "status": "error"
        }
    except requests.exceptions.ConnectionError:
        return {
            "response": "Không thể kết nối đến server. Vui lòng kiểm tra lại backend API.",
            "logs": [],
            "processing_time": 0,
            "turns_processed": 0,
            "status": "error"
        }
    except Exception as e:
        return {
            "response": f"Đã xảy ra lỗi: {str(e)}",
            "logs": [],
            "processing_time": 0,
            "turns_processed": 0,
            "status": "error"
        }


def display_message(role: str, content: str, logs: List[Dict] = None, processing_info: Dict = None):
    """Display a message with appropriate styling and optional logs."""
    if role == "user":
        st.chat_message("user").write(f"🎓 **Gia sư:** {content}")
        
    elif role == "assistant":
        with st.chat_message("assistant"):
            st.write(f"🤖 **ISY:** {content}")
            
            # Display processing information if available
            if processing_info:
                st.success(f"""
                📊 **Thống kê xử lý:**
                - ⏱️ Thời gian: **{processing_info.get('processing_time', 0):.2f} giây**
                - 🔄 Số vòng: **{processing_info.get('turns_processed', 0)}**
                - ✅ Trạng thái: **{processing_info.get('status', 'unknown').upper()}**
                """)
            
            # Display logs if available
            if logs:
                with st.expander(f"🔍 Chi tiết quá trình xử lý ({len(logs)} bước)", expanded=False):
                    display_logs(logs)
                    
    elif role == "processing":
        st.info(f"⏳ **Hệ thống:** {content}")


def display_logs(logs: List[Dict]):
    """Display detailed processing logs using Streamlit native components."""
    if not logs:
        st.info("Không có log nào để hiển thị")
        return
    
    # Create a nice timeline using Streamlit components
    st.markdown("### 📋 Timeline Xử Lý:")
    
    # First, show the timeline overview
    for i, log in enumerate(logs):
        timestamp = log.get('timestamp', '')
        if timestamp:
            # Format timestamp to show only time
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                time_str = dt.strftime('%H:%M:%S')
            except:
                time_str = timestamp[-8:]  # Get last 8 chars as fallback
        else:
            time_str = ""
        
        status = log.get('status', 'info')
        message = log.get('message', '')
        
        # Choose emoji and color based on status
        if status == 'processing':
            status_emoji = "🟡"
            status_color = "orange"
        elif status == 'success':
            status_emoji = "🟢"
            status_color = "green"
        elif status == 'error':
            status_emoji = "🔴"
            status_color = "red"
        else:  # info
            status_emoji = "🔵"
            status_color = "blue"
        
        # Create columns for better layout
        col1, col2, col3 = st.columns([1, 1, 8])
        
        with col1:
            st.text(time_str)
        
        with col2:
            st.markdown(f":{status_color}[{status_emoji}]")
        
        with col3:
            st.markdown(f"**{message}**")
        
        # Add a subtle divider except for the last item
        if i < len(logs) - 1:
            st.markdown("---")
    
    # Then show detailed information separately (not nested in expander)
    st.markdown("---")
    show_details = st.checkbox("🔍 Hiển thị chi tiết từng bước", key=f"show_log_details_{len(logs)}_{hash(str(logs))}")
    
    if show_details:
        st.markdown("### 📊 Chi tiết từng bước:")
        
        for i, log in enumerate(logs):
            step = log.get('step', 'unknown')
            details = log.get('details', {})
            
            if details:
                st.markdown(f"**Bước {i+1}: {step}**")
                
                # Format details nicely
                for key, value in details.items():
                    if key == 'function_name':
                        st.markdown(f"🔧 **Function:** `{value}`")
                    elif key == 'arguments':
                        st.markdown("📥 **Arguments:**")
                        st.json(value)
                    elif key == 'result_preview':
                        st.markdown("📤 **Result Preview:**")
                        st.code(value, language="text")
                    else:
                        st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
                
                if i < len([l for l in logs if l.get('details')]) - 1:
                    st.markdown("---")


def main():
    """Main application function."""
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.title("🎓 ISY Tutor Command Center")
    st.caption("Giao diện điều khiển thông minh cho Gia sư - Sử dụng ngôn ngữ tự nhiên để quản lý học sinh")
    
    # Check API health
    if not st.session_state.api_available:
        st.error("⚠️ Backend API không khả dụng. Vui lòng khởi động server FastAPI trước khi sử dụng.")
        if st.button("🔄 Kiểm tra lại kết nối"):
            st.session_state.api_available = check_api_health()
            st.rerun()
        return
    
    # Display API status
    st.success("✅ Kết nối Backend API thành công!")
    
    # Display chat history
    st.subheader("💬 Lịch sử cuộc trò chuyện")
    
    # Container for messages
    message_container = st.container()
    
    with message_container:
        for message in st.session_state.messages:
            if message["role"] == "assistant":
                display_message(
                    message["role"], 
                    message["content"],
                    logs=message.get("logs"),
                    processing_info=message.get("processing_info")
                )
            else:
                display_message(message["role"], message["content"])
    
    # Example commands
    st.sidebar.header("📝 Ví dụ lệnh")
    st.sidebar.markdown("""
    **Giao bài tập:**
    - Giao cho An 3 bài tập về giải hệ phương trình bằng phương pháp thế
    - Cho Bình làm 5 bài tập về tứ giác nội tiếp
    
    **Xem hoạt động:**
    - Xem lại hoạt động của An hôm nay
    - Kiểm tra log hoạt động của Bình
    
    **Kết hợp:**
    - Giao cho An 3 bài tập về giải hệ phương trình và xem hoạt động của bạn ấy
    """)
    
    # Chat input
    if prompt := st.chat_input("Nhập lệnh của bạn tại đây... (ví dụ: Giao cho An 3 bài tập về giải hệ phương trình)"):
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with message_container:
            display_message("user", prompt)
        
        # Show processing message
        with message_container:
            processing_placeholder = st.empty()
            with processing_placeholder:
                display_message("processing", "ISY đang xử lý yêu cầu của bạn...")
        
        # Send to API and get response
        response_data = send_command_to_api(prompt)
        
        # Remove processing message
        processing_placeholder.empty()
        
        # Parse response if it's a dictionary (new format) or string (old format)
        if isinstance(response_data, dict):
            response_text = response_data.get("response", "Không nhận được phản hồi")
            logs = response_data.get("logs", [])
            processing_info = {
                "processing_time": response_data.get("processing_time", 0),
                "turns_processed": response_data.get("turns_processed", 0),
                "status": response_data.get("status", "unknown")
            }
        else:
            # Fallback for old string format
            response_text = response_data
            logs = []
            processing_info = None
        
        # Add assistant response to history with logs
        assistant_message = {
            "role": "assistant", 
            "content": response_text,
            "logs": logs,
            "processing_info": processing_info
        }
        st.session_state.messages.append(assistant_message)
        
        # Display assistant response with logs
        with message_container:
            display_message("assistant", response_text, logs=logs, processing_info=processing_info)
        
        # Rerun to update the interface
        st.rerun()
    
    # Clear chat button
    if st.button("🗑️ Xóa lịch sử chat"):
        st.session_state.messages = []
        st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("💡 **Hướng dẫn sử dụng:** Nhập các lệnh bằng ngôn ngữ tự nhiên để quản lý học sinh, giao bài tập, và theo dõi hoạt động học tập.")


if __name__ == "__main__":
    main()