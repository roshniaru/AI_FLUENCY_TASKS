
"""Day 8: Agentic RAG Helpdesk - Complete Assignment"""

import ast
import operator
import os
import re
from pathlib import Path

from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from lc_config import (
    get_model,
    get_vectorstore,
    PROVIDER,
    EMBED_PROVIDER,
)

# --------------------------------------------------
# 1. CONFIGURATION
# --------------------------------------------------

COURSE_FEES = {
    "CS101": 12000,
    "AI202": 18000,
    "DS303": 15000,
}

MAX_DISTANCE = 0.4
store = get_vectorstore()


# --------------------------------------------------
# 2. HANDBOOK SEARCH TOOL WITH DISTANCE FILTERING
# --------------------------------------------------

@tool
def search_handbook(query: str) -> str:
    """Search the college handbook and return only relevant passages."""

    results = store.similarity_search_with_score(query, k=3)

    relevant_docs = [
        (doc, score)
        for doc, score in results
        if score <= MAX_DISTANCE
    ]

    if not relevant_docs:
        return "NO_MATCH: this is not covered in the college handbook."

    return "\n\n".join(
        f"[{doc.metadata.get('source', 'unknown')}] "
        f"{doc.page_content}"
        for doc, score in relevant_docs
    )


# --------------------------------------------------
# 3. EXAM ELIGIBILITY TOOL
# --------------------------------------------------

@tool
def check_exam_eligibility(attendance_percent: float) -> str:
    """Check exam eligibility for attendance between 0 and 100 percent."""

    if attendance_percent < 0 or attendance_percent > 100:
        return (
            "ERROR: Attendance percentage must be "
            "between 0 and 100."
        )

    if attendance_percent >= 75:
        return "ELIGIBLE: You can write the end-semester exam."

    if attendance_percent >= 65:
        return "CONDONATION: You need to pay Rs. 500 per course."

    return (
        "NOT ELIGIBLE: Attendance below 65% is "
        "insufficient to write the end-semester exam."
    )


# --------------------------------------------------
# 4. COURSE FEE TOOL
# --------------------------------------------------

@tool
def get_course_fee(course_code: str) -> str:
    """Get the fee in rupees for CS101, AI202 or DS303."""

    code = course_code.strip().upper()
    fee = COURSE_FEES.get(code)

    if fee is not None:
        return f"{code} fee is Rs. {fee}"

    return f"Unknown course code: {course_code}"


# --------------------------------------------------
# 5. CALCULATOR TOOL
# --------------------------------------------------

OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}


@tool
def calculator(expression: str) -> str:
    """Calculate arithmetic expressions using numbers and +, -, *, /."""

    def evaluate(node):
        if (
            isinstance(node, ast.Constant)
            and isinstance(node.value, (int, float))
        ):
            return node.value

        if isinstance(node, ast.BinOp) and type(node.op) in OPS:
            return OPS[type(node.op)](
                evaluate(node.left),
                evaluate(node.right),
            )

        raise ValueError("Only +, -, *, / and numbers are allowed.")

    try:
        tree = ast.parse(expression, mode="eval")
        return str(evaluate(tree.body))
    except Exception as error:
        return f"Error: {error}"



tools = [
    search_handbook,
    get_course_fee,
    calculator,
    check_exam_eligibility,
]

model = get_model().bind_tools(tools)




SYSTEM = """
You are the Greenfield College Helpdesk Agent.

Your job is to answer questions using the college handbook and the
available tools. Be accurate, concise, and never invent college policies.

RULES:

1. COLLEGE HANDBOOK
   - Use search_handbook for questions about college policies,
     placements, fees, attendance rules, hostel rules, and other
     information that may be covered by the handbook.
   - Mention the source filename when available.
   - Do not invent or assume information that is not supported
     by the handbook.

2. PLACEMENT ELIGIBILITY
   - For questions about placement eligibility, call search_handbook.
   - Answer using the retrieved policy.
   - The placement policy requires a CGPA of 6.5 or above
     and no standing arrears.

3. EXAM ATTENDANCE ELIGIBILITY
   - For questions about exam eligibility based on attendance,
     ALWAYS call check_exam_eligibility.
   - Do not calculate or guess the eligibility result yourself.
   - Follow the tool result exactly:
       * Attendance outside 0 to 100: report the input error.
       * Attendance >= 75%: ELIGIBLE.
       * Attendance >= 65% and < 75%: CONDONATION of Rs. 500 per course.
       * Attendance < 65%: NOT ELIGIBLE.

4. COURSE FEES AND LATE FEES
   - For course fee questions, call get_course_fee for each
     requested course.
   - For late-fee rules, call search_handbook.
   - Use the calculator tool to calculate totals.
   - The late fee is Rs. 100 per day, up to a maximum of
     Rs. 2,000 per semester.
   - Do not guess fee amounts. Use tool results.

5. FOLLOW-UP QUESTIONS AND MEMORY
   - Use the conversation history to understand follow-up questions.
   - Preserve relevant details from earlier messages.
   - For example, if the user asks about paying five days late
     after asking for the maximum late fee, calculate the total
     using five days of late fees instead of the maximum late fee.
   - Do not ask the user to repeat information already available
     in the conversation.

6. QUESTIONS UNRELATED TO COLLEGE POLICIES
   - For every question unrelated to college policies, you MUST
     call search_handbook before answering.
   - Never answer an unrelated question from your own knowledge
     without first calling search_handbook.
   - If search_handbook returns text beginning with "NO_MATCH:",
     answer exactly:
     I don't know.
   - Do not add explanations, facts, or extra words to that answer.
   - If search_handbook returns relevant information, answer only
     using that information.

7. TOOL USAGE
   - Use the appropriate tool whenever a rule above requires it.
   - Do not claim that a tool was called unless it was actually called.
   - Do not invent tool results.
   - Use the calculator for arithmetic when instructed above.

8. RESPONSE STYLE
   - Answer clearly and briefly.
   - Mention the handbook source filename when available.
   - If information is unavailable, say so according to the rules above.
"""




def agent(state: MessagesState):
    response = model.invoke(
        [("system", SYSTEM)] + state["messages"]
    )
    return {"messages": [response]}


builder = StateGraph(MessagesState)
builder.add_node("agent", agent)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)
builder.add_edge("tools", "agent")

graph = builder.compile(checkpointer=InMemorySaver())



def ask(question: str, thread_id: str):
    config = {
        "configurable": {"thread_id": thread_id},
        "recursion_limit": 15,
    }

    called_tools = []
    final_answer = ""

    print(f"\n[{thread_id}] USER: {question}")

    for step in graph.stream(
        {"messages": [("user", question)]},
        config,
        stream_mode="updates",
    ):
        for node, update in step.items():
            for message in update.get("messages", []):

                if getattr(message, "tool_calls", None):
                    for call in message.tool_calls:
                        name = call["name"]
                        args = call["args"]
                        called_tools.append(name)
                        print(
                            f"   {node} -> "
                            f"call {name}({args})"
                        )

                elif node == "tools":
                    print(
                        f"   tools -> {message.name} returned "
                        f"{str(message.content)[:250]!r}"
                    )

                else:
                    final_answer = str(message.content)
                    print(f"   ANSWER: {final_answer}")

    return called_tools, final_answer



def get_top_score(question: str):
    results = store.similarity_search_with_score(question, k=3)

    if not results:
        return None, []

    details = [
        (round(float(score), 3), doc.metadata.get("source", "unknown"))
        for doc, score in results
    ]

    return round(float(results[0][1]), 3), details


# --------------------------------------------------
# 11. CREATE RESULTS.MD
# --------------------------------------------------

def normalized(text: str) -> str:
    return re.sub(r"[\s,]", "", text.lower())


def write_results(records, placement_score, france_score,
                  placement_details, france_details):

    rows = []

    for number, question, called_tools, answer, expected in records:
        actual = normalized(answer)
        correct = all(
            normalized(item) in actual
            for item in expected
        )

        tools_text = (
            " -> ".join(called_tools)
            if called_tools
            else "None"
        )

        reason = "" if correct else "Expected answer not detected."

        rows.append(
            f"| {number} | {tools_text} | "
            f"{answer.replace('|', '/').replace(chr(10), ' ')} | "
            f"{'Y' if correct else 'N'} | {reason} |"
        )

    placement_text = ", ".join(
        f"{score} ({source})"
        for score, source in placement_details
    )
    france_text = ", ".join(
        f"{score} ({source})"
        for score, source in france_details
    )

    model_name = (
        os.getenv("MODEL_NAME")
        or os.getenv("GROQ_MODEL")
        or os.getenv("OPENAI_MODEL")
        or "See get_model() in lc_config.py"
    )

    content = f"""# Day 8 - Agentic RAG Results

## Configuration

- Provider: {PROVIDER}
- Model: {model_name}
- Embedding provider: {EMBED_PROVIDER}
- MAX_DISTANCE: {MAX_DISTANCE}

## Retrieval Distance Scores

- Placement question top score: {placement_score}
- Placement top 3: {placement_text}
- France question top score: {france_score}
- France top 3: {france_text}

## Agent Test Results

| # | Tools called (in order) | Agent's answer (short) | Correct? (Y/N) | If N, why? |
|---|---|---|---|---|
{chr(10).join(rows)}
"""

    Path("results.md").write_text(content, encoding="utf-8")
    print("\nCreated results.md")


# --------------------------------------------------
# 12. MAIN: ASSIGNMENT TESTS
# --------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("DAY 8 - AGENTIC RAG HELPDESK")
    print("=" * 60)

    # Test exam eligibility tool independently.
    print("\n--- EXAM ELIGIBILITY TOOL TESTS ---")

    for attendance in [82, 70, 50, 120]:
        result = check_exam_eligibility.invoke(
            {"attendance_percent": attendance}
        )
        print(f"{attendance}% -> {result}")

    # Print the graph structure.
    print("\n--- AGENT GRAPH ---")
    print(graph.get_graph().draw_mermaid())

    # Measure scores before running the questions.
    placement_question = (
        "What CGPA do I need to be eligible for placements?"
    )
    france_question = "What is the capital of France?"

    placement_score, placement_details = get_top_score(
        placement_question
    )
    france_score, france_details = get_top_score(france_question)

    print("\n--- RETRIEVAL SCORES ---")
    print("MAX_DISTANCE:", MAX_DISTANCE)
    print("Placement:", placement_details)
    print("France:", france_details)

    # All five questions share one thread to test memory.
    thread_id = "task-run"

    tests = [
        (
            1,
            "What CGPA do I need to be eligible for placements?",
            ["6.5"],
        ),
        (
            2,
            "My attendance is 70%. Can I write the exam?",
            ["500"],
        ),
        (
            3,
            "What is the total of the CS101 fee, the AI202 fee "
            "and the maximum late fee?",
            ["32000"],
        ),
        (
            4,
            "And if I pay only 5 days late instead?",
            ["30500"],
        ),
        (
            5,
            "What is the capital of France?",
            ["i don't know"],
        ),
    ]

    records = []

    for number, question, expected in tests:
        called_tools, answer = ask(question, thread_id)

        records.append(
            (number, question, called_tools, answer, expected)
        )

    # Save the results table.
    write_results(
        records,
        placement_score,
        france_score,
        placement_details,
        france_details,
    )

    # Display saved memory count.
    saved_state = graph.get_state(
        {"configurable": {"thread_id": thread_id}}
    )
    saved_messages = saved_state.values.get("messages", [])

    print(
        f"\nThread '{thread_id}' has "
        f"{len(saved_messages)} messages saved in memory."
    )
    print("\nAssignment run completed.")
