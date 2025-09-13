import json
import os
from datetime import datetime
from typing import Dict, List, Any


def _read_json(filepath: str) -> List[Dict[str, Any]]:
    """Read JSON data from file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _write_json(filepath: str, data: List[Dict[str, Any]]) -> None:
    """Write JSON data to file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _log_activity(student_id: str, activity: str, details: Dict[str, Any]) -> None:
    """Log student activity to activity logs file."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "student_id": student_id,
        "activity": activity,
        "details": details
    }
    
    logs_path = os.path.join("data", "mock_activity_logs.json")
    logs = _read_json(logs_path)
    logs.append(log_entry)
    _write_json(logs_path, logs)


def validate_and_suggest_missing_info(function_name: str, provided_args: Dict[str, Any]) -> str:
    """
    Validate function arguments and suggest missing information.
    
    Args:
        function_name: Name of the function being called
        provided_args: Arguments provided by the user
        
    Returns:
        Empty string if valid, or suggestion message if missing info
    """
    suggestions = {
        "assign_exercise": {
            "required": ["student_name", "learning_object_title", "num_questions"],
            "suggestions": {
                "student_name": "Vui lòng cho biết tên học sinh cần giao bài tập.",
                "learning_object_title": "Vui lòng cho biết chủ đề/nội dung bài tập (ví dụ: 'giải hệ phương trình', 'tứ giác nội tiếp').",
                "num_questions": "Vui lòng cho biết số lượng câu hỏi cần giao (ví dụ: 5 câu)."
            }
        },
        "grade_submission": {
            "required": ["submission_id", "score", "feedback_text"],
            "suggestions": {
                "submission_id": "Vui lòng cung cấp mã ID của bài nộp cần chấm (ví dụ: 'sub_001').",
                "score": "Vui lòng cho biết điểm số (từ 0 đến 100).",
                "feedback_text": "Vui lòng cung cấp nhận xét/feedback cho học sinh."
            }
        },
        "add_note_to_report": {
            "required": ["student_name", "note_text"],
            "suggestions": {
                "student_name": "Vui lòng cho biết tên học sinh cần thêm ghi chú.",
                "note_text": "Vui lòng cung cấp nội dung ghi chú muốn thêm vào báo cáo."
            }
        },
        "create_custom_pathway": {
            "required": ["student_name", "learning_object_titles"],
            "suggestions": {
                "student_name": "Vui lòng cho biết tên học sinh cần tạo lộ trình.",
                "learning_object_titles": "Vui lòng liệt kê các chủ đề học tập muốn đưa vào lộ trình (ví dụ: ['giải hệ phương trình', 'tứ giác nội tiếp'])."
            }
        }
    }
    
    if function_name not in suggestions:
        return ""
    
    config = suggestions[function_name]
    missing = []
    
    for required_param in config["required"]:
        if required_param not in provided_args or not provided_args[required_param]:
            missing.append(config["suggestions"][required_param])
    
    if missing:
        return "Để thực hiện yêu cầu này, em cần thêm thông tin:\n" + "\n".join(f"- {msg}" for msg in missing)
    
    return ""


def list_available_submissions() -> str:
    """
    List all available submissions that can be graded.
    
    Returns:
        JSON string with list of submissions
    """
    submissions_path = os.path.join("data", "mock_submissions.json")
    submissions = _read_json(submissions_path)
    
    if not submissions:
        return "Hiện tại không có bài nộp nào để chấm."
    
    available_submissions = []
    for sub in submissions:
        if sub.get("status") == "submitted":
            available_submissions.append({
                "id": sub["id"],
                "student_name": sub["student_name"],
                "submitted_date": sub.get("submitted_date", "N/A"),
                "content_preview": sub.get("content", "")[:100] + "..." if len(sub.get("content", "")) > 100 else sub.get("content", "")
            })
    
    if not available_submissions:
        return "Tất cả bài nộp đã được chấm điểm."
    
    return json.dumps({
        "message": f"Tìm thấy {len(available_submissions)} bài nộp chưa chấm:",
        "submissions": available_submissions
    }, ensure_ascii=False, indent=2)


def assign_exercise(student_name: str, learning_object_title: str, num_questions: int) -> str:
    """
    Assign exercises to a student based on learning object title.
    
    Args:
        student_name: The name of the student to assign exercises to
        learning_object_title: The title of the learning object/topic
        num_questions: Number of questions to assign
    
    Returns:
        Success or error message
    """
    # Find student by name
    students_path = os.path.join("data", "mock_students.json")
    students = _read_json(students_path)
    
    student = None
    for s in students:
        if s["name"].lower() == student_name.lower():
            student = s
            break
    
    if not student:
        return f"Không tìm thấy học sinh có tên '{student_name}'"
    
    # Find learning object by title
    lo_path = os.path.join("data", "mock_learning_objects.json")
    learning_objects = _read_json(lo_path)
    
    learning_object = None
    for lo in learning_objects:
        if learning_object_title.lower() in lo["title"].lower() or lo["title"].lower() in learning_object_title.lower():
            learning_object = lo
            break
    
    if not learning_object:
        return f"Không tìm thấy chủ đề học tập '{learning_object_title}'"
    
    # Create assignment
    assignment = {
        "id": f"assignment_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "student_id": student["id"],
        "student_name": student["name"],
        "learning_object_id": learning_object["id"],
        "learning_object_title": learning_object["title"],
        "num_questions": num_questions,
        "assigned_date": datetime.now().isoformat(),
        "status": "assigned"
    }
    
    # Save assignment
    assignments_path = os.path.join("data", "mock_assignments.json")
    assignments = _read_json(assignments_path)
    assignments.append(assignment)
    _write_json(assignments_path, assignments)
    
    # Log activity
    _log_activity(
        student["id"],
        "assignment_created",
        {
            "learning_object": learning_object["title"],
            "num_questions": num_questions,
            "assignment_id": assignment["id"]
        }
    )
    
    return f"Đã giao thành công {num_questions} bài tập về '{learning_object['title']}' cho học sinh {student['name']}"


def get_student_activity_log(student_name: str, date_range: str = "today") -> str:
    """
    Get activity log for a specific student.
    
    Args:
        student_name: The name of the student
        date_range: Date range filter (e.g., "today", "this_week", etc.)
    
    Returns:
        JSON string with activity logs or message if no logs found
    """
    # Find student by name
    students_path = os.path.join("data", "mock_students.json")
    students = _read_json(students_path)
    
    student = None
    for s in students:
        if s["name"].lower() == student_name.lower():
            student = s
            break
    
    if not student:
        return f"Không tìm thấy học sinh có tên '{student_name}'"
    
    # Get activity logs
    logs_path = os.path.join("data", "mock_activity_logs.json")
    logs = _read_json(logs_path)
    
    # Filter logs for this student
    student_logs = [log for log in logs if log.get("student_id") == student["id"]]
    
    if not student_logs:
        return f"Không có hoạt động nào được ghi nhận cho học sinh {student['name']}"
    
    # For simplicity, we'll return all logs for now
    # In a real system, you'd filter by date_range
    return json.dumps({
        "student_name": student["name"],
        "total_activities": len(student_logs),
        "activities": student_logs
    }, ensure_ascii=False, indent=2)


def grade_submission(submission_id: str, score: float, feedback_text: str) -> str:
    """
    Grade a student submission and provide feedback.
    
    Args:
        submission_id: The ID of the submission to grade
        score: The score to assign (0-100)
        feedback_text: Detailed feedback text for the student
    
    Returns:
        Success or error message
    """
    submissions_path = os.path.join("data", "mock_submissions.json")
    submissions = _read_json(submissions_path)
    
    # Find submission
    submission = None
    for i, sub in enumerate(submissions):
        if sub["id"] == submission_id:
            submission = sub
            submission_index = i
            break
    
    if not submission:
        return f"Không tìm thấy bài nộp có ID '{submission_id}'"
    
    # Validate score
    if not (0 <= score <= 100):
        return "Điểm số phải nằm trong khoảng 0-100"
    
    # Update submission
    submissions[submission_index].update({
        "score": score,
        "feedback": feedback_text,
        "status": "graded",
        "graded_date": datetime.now().isoformat()
    })
    
    # Save updated submissions
    _write_json(submissions_path, submissions)
    
    # Log activity
    _log_activity(
        submission["student_id"],
        "submission_graded",
        {
            "submission_id": submission_id,
            "score": score,
            "feedback_preview": feedback_text[:50] + "..." if len(feedback_text) > 50 else feedback_text
        }
    )
    
    return f"Đã chấm điểm thành công bài nộp của {submission['student_name']}: {score}/100 điểm"


def add_note_to_report(student_name: str, note_text: str) -> str:
    """
    Add a tutor note to student's progress report.
    
    Args:
        student_name: The name of the student
        note_text: The note text to add
    
    Returns:
        Success or error message
    """
    # Find student
    students_path = os.path.join("data", "mock_students.json")
    students = _read_json(students_path)
    
    student = None
    for s in students:
        if s["name"].lower() == student_name.lower():
            student = s
            break
    
    if not student:
        return f"Không tìm thấy học sinh có tên '{student_name}'"
    
    # Get and update student report
    reports_path = os.path.join("data", "mock_student_reports.json")
    reports = _read_json(reports_path)
    
    # Find or create report
    report = None
    report_index = -1
    for i, rep in enumerate(reports):
        if rep["student_id"] == student["id"]:
            report = rep
            report_index = i
            break
    
    if not report:
        # Create new report
        report = {
            "student_id": student["id"],
            "student_name": student["name"],
            "overall_progress": 0,
            "strengths": [],
            "weaknesses": [],
            "tutor_notes": []
        }
        reports.append(report)
        report_index = len(reports) - 1
    
    # Add note with timestamp
    note_entry = {
        "timestamp": datetime.now().isoformat(),
        "note": note_text,
        "tutor": "Admin"  # In real system, get from session
    }
    
    reports[report_index]["tutor_notes"].append(note_entry)
    
    # Save updated reports
    _write_json(reports_path, reports)
    
    # Log activity
    _log_activity(
        student["id"],
        "note_added_to_report",
        {
            "note_preview": note_text[:50] + "..." if len(note_text) > 50 else note_text,
            "total_notes": len(reports[report_index]["tutor_notes"])
        }
    )
    
    return f"Đã thêm ghi chú vào báo cáo của {student['name']}. Tổng số ghi chú: {len(reports[report_index]['tutor_notes'])}"


def create_custom_pathway(student_name: str, learning_object_titles: List[str]) -> str:
    """
    Create a custom learning pathway for a student.
    
    Args:
        student_name: The name of the student
        learning_object_titles: List of learning object titles to include in pathway
    
    Returns:
        Success or error message
    """
    # Find student
    students_path = os.path.join("data", "mock_students.json")
    students = _read_json(students_path)
    
    student = None
    for s in students:
        if s["name"].lower() == student_name.lower():
            student = s
            break
    
    if not student:
        return f"Không tìm thấy học sinh có tên '{student_name}'"
    
    # Find learning objects
    lo_path = os.path.join("data", "mock_learning_objects.json")
    learning_objects = _read_json(lo_path)
    
    matched_los = []
    not_found = []
    
    for title in learning_object_titles:
        found = False
        for lo in learning_objects:
            if title.lower() in lo["title"].lower() or lo["title"].lower() in title.lower():
                if lo not in matched_los:  # Avoid duplicates
                    matched_los.append(lo)
                found = True
                break
        if not found:
            not_found.append(title)
    
    if not matched_los:
        return f"Không tìm thấy chủ đề học tập nào phù hợp trong danh sách: {', '.join(learning_object_titles)}"
    
    # Create pathway
    pathway = {
        "id": f"pathway_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "student_id": student["id"],
        "student_name": student["name"],
        "title": f"Lộ trình tùy chỉnh cho {student['name']}",
        "learning_objects": matched_los,
        "created_date": datetime.now().isoformat(),
        "status": "active",
        "completion_progress": 0
    }
    
    # Save pathway
    pathways_path = os.path.join("data", "mock_custom_pathways.json")
    pathways = _read_json(pathways_path)
    pathways.append(pathway)
    _write_json(pathways_path, pathways)
    
    # Log activity
    _log_activity(
        student["id"],
        "custom_pathway_created",
        {
            "pathway_id": pathway["id"],
            "total_learning_objects": len(matched_los),
            "learning_objects": [lo["title"] for lo in matched_los]
        }
    )
    
    result_msg = f"Đã tạo lộ trình tùy chỉnh cho {student['name']} với {len(matched_los)} chủ đề học tập"
    
    if not_found:
        result_msg += f"\nLưu ý: Không tìm thấy các chủ đề: {', '.join(not_found)}"
    
    return result_msg