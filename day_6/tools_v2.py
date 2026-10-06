"""Day 6: College Attendance and Fine Assistant tools."""

import ast
import operator


# Sample college data
ATTENDANCE = {
    "7376252AL203": {
        "odd": 92,
        "even": 88
    },
    "7376252AL204": {
        "odd": 76,
        "even": 81
    }
}


# -----------------------------
# Tool 1: Get Attendance
# -----------------------------
def get_attendance(student_id: str, semester: str = "odd") -> str:
    """Return attendance percentage for a student."""

    student = ATTENDANCE.get(student_id.strip())

    if student is None:
        return f"Unknown student ID: {student_id}."

    attendance = student.get(semester)

    if attendance is None:
        return f"No attendance data for semester: {semester}."

    return str(attendance)


# -----------------------------
# Tool 2: Calculate Fine
# -----------------------------
def calculate_fine(days_absent: int) -> str:
    """Calculate attendance fine based on absent days."""

    if days_absent < 0:
        return "Days absent cannot be negative."

    fine = days_absent * 50

    return str(fine)


# -----------------------------
# Tool mapping
# -----------------------------
TOOL_FUNCTIONS = {
    "get_attendance": get_attendance,
    "calculate_fine": calculate_fine,
}


# -----------------------------
# Tool schemas
# -----------------------------
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_attendance",
            "description": (
                "Get attendance percentage for one student. "
                "Valid semesters are odd and even."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "student_id": {
                        "type": "string",
                        "description": "Student ID such as 7376252AL203"
                    },
                    "semester": {
                        "type": "string",
                        "enum": ["odd", "even"],
                        "description": "Semester type"
                    }
                },
                "required": ["student_id"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_fine",
            "description": (
                "Calculate the fine for the number of absent days. "
                "Fine is Rs.50 per absent day."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "days_absent": {
                        "type": "integer",
                        "description": "Number of days the student was absent"
                    }
                },
                "required": ["days_absent"],
                "additionalProperties": False
            }
        }
    }
]


# One source of truth for validation
SCHEMAS = {
    tool["function"]["name"]: tool["function"]["parameters"]
    for tool in TOOLS
}