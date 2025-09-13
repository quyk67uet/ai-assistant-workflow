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