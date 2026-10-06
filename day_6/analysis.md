# Day 6 – Reliable Tool Calling: Schemas, Validation, Retry and Structured Outputs

## 1. Objective

The objective of this lab is to build a reliable tool-calling system using an OpenAI-compatible API.

The system demonstrates:

- Tool calling
- JSON Schema based tool definitions
- Argument validation
- Tool lookup and execution
- Retry handling
- Repeated-call protection
- Multiple tool calls
- Deliberate fault injection
- Structured output comparison

For this implementation, a college attendance and fine scenario was selected instead of the course-fee scenario.

The implementation uses Groq through its OpenAI-compatible API.

The Day 6 task requires an own scenario, at least two tools, schema-based validation, deliberate fault injection, a robust agent, and comparison of unconstrained, JSON, and JSON Schema outputs.


## 2. Scenario

### College Attendance and Fine Assistant

The system provides two tools:

### Tool 1 – get_attendance

This tool returns the attendance percentage of a student.

Arguments:

- `student_id`
- `semester`

The valid semester values are:

- `odd`
- `even`

Example data:

- Student `7376252AL203`
  - Odd semester: 92%
  - Even semester: 88%

- Student `7376252AL204`
  - Odd semester: 76%
  - Even semester: 81%

### Tool 2 – calculate_fine

This tool calculates the fine based on the number of absent days.

The fine is Rs.50 per absent day.

For example:

```text
3 absent days × Rs.50 = Rs.150