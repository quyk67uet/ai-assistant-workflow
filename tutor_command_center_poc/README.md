# ISY Tutor Command Center - Proof of Concept

## Mô tả dự án
Đây là một Proof of Concept cho tính năng "Tutor's Command Center" - một giao diện chat cho phép Gia sư quản lý học sinh bằng các lệnh ngôn ngữ tự nhiên. Hệ thống sử dụng AI Agent với Gemini API để hiểu và xử lý các lệnh của gia sư.

## Cấu trúc dự án
```
tutor_command_center_poc/
├── data/                              # Dữ liệu giả lập
│   ├── mock_students.json            # Danh sách học sinh
│   ├── mock_learning_objects.json    # Danh sách chủ đề học tập
│   ├── mock_activity_logs.json       # Log hoạt động (rỗng ban đầu)
│   └── mock_assignments.json         # Bài tập đã giao (rỗng ban đầu)
├── app/                               # Backend FastAPI
│   ├── __init__.py
│   ├── main.py                       # FastAPI server
│   ├── agent.py                      # AI Agent với Gemini
│   └── tools.py                      # Công cụ xử lý dữ liệu
├── frontend.py                        # Giao diện Streamlit
├── requirements.txt                   # Dependencies
├── .env                              # API keys
└── README.md                         # File này
```

## Hướng dẫn cài đặt và chạy

### 1. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 2. Cấu hình API Key
Mở file `.env` và thay thế `YOUR_GEMINI_API_KEY_HERE` bằng API key thật từ Google AI Studio.

### 3. Chạy Backend (Terminal 1)
```bash
cd tutor_command_center_poc
uvicorn app.main:app --reload
```
Backend sẽ chạy tại: http://127.0.0.1:8000

### 4. Chạy Frontend (Terminal 2)
```bash
cd tutor_command_center_poc
streamlit run frontend.py
```
Frontend sẽ chạy tại: http://localhost:8501

## Kịch bản kiểm tra

### Lệnh test mẫu:
```
Giao cho An 3 bài tập về giải hệ phương trình bằng phương pháp thế và xem lại hoạt động của bạn ấy hôm nay
```

### Kết quả mong đợi:
1. Hệ thống sẽ tạo bài tập mới trong `mock_assignments.json`
2. Ghi log hoạt động vào `mock_activity_logs.json`
3. Trả về thông báo thành công và hiển thị hoạt động của học sinh An

## Các tính năng chính

### AI Agent (app/agent.py)
- Tích hợp Gemini 1.5 Flash với Function Calling
- Xử lý lệnh ngôn ngữ tự nhiên
- Tự động chọn công cụ phù hợp để thực thi

### Tools (app/tools.py)
- `assign_exercise()`: Giao bài tập cho học sinh
- `get_student_activity_log()`: Xem log hoạt động học sinh
- Các hàm helper để thao tác với dữ liệu JSON

### Backend API (app/main.py)
- FastAPI server với endpoint `/tutor-command`
- CORS support cho Streamlit
- Error handling toàn diện

### Frontend (frontend.py)
- Giao diện chat thân thiện
- Real-time communication với backend
- Hiển thị lịch sử cuộc trò chuyện
- Ví dụ lệnh và hướng dẫn sử dụng

## Dữ liệu mẫu

### Học sinh:
- An (student_01)
- Bình (student_02)

### Chủ đề học tập:
- "Dấu hiệu nhận biết tứ giác nội tiếp" (LO-C8-04)
- "Giải hệ phương trình bằng phương pháp thế" (LO-C1-07)

## Troubleshooting

### Lỗi API Key:
- Kiểm tra file `.env` có chứa API key hợp lệ
- Đảm bảo API key có quyền truy cập Gemini API

### Lỗi kết nối:
- Đảm bảo backend đang chạy trước khi khởi động frontend
- Kiểm tra port 8000 và 8501 không bị chiếm bởi ứng dụng khác

### Lỗi dữ liệu:
- Kiểm tra các file JSON trong thư mục `data/` có đúng định dạng
- Đảm bảo quyền ghi file cho thư mục dự án