# Day 8 - Agentic RAG Results

## Configuration

- Provider: groq
- Model: See get_model() in lc_config.py
- Embedding provider: fastembed
- MAX_DISTANCE: 0.4

## Retrieval Distance Scores

- Placement question top score: 0.177
- Placement top 3: 0.177 (placement_policy.md), 0.236 (fee_policy.md), 0.284 (placement_policy.md)
- France question top score: 0.573
- France top 3: 0.573 (hostel_rules.md), 0.573 (hostel_rules.md), 0.577 (library.md)

## Agent Test Results

| # | Tools called (in order) | Agent's answer (short) | Correct? (Y/N) | If N, why? |
|---|---|---|---|---|
| 1 | search_handbook | You need a CGPA of **6.5 or higher** to be eligible for campus placements. (Source: placement_policy.md) | Y |  |
| 2 | check_exam_eligibility | You are **eligible with a condonation** – you need to pay a condonation fee of **Rs 500 per course**. | Y |  |
| 3 | get_course_fee -> get_course_fee -> search_handbook -> calculator | The total is **Rs 32,000** (CS101 = Rs 12,000, AI202 = Rs 18,000, maximum late fee = Rs 2,000). (Source: fee_policy.md) | Y |  |
| 4 | calculator | If you’re only 5 days late, the late fee is 5 × Rs 100 = Rs 500.   So the total becomes **Rs 30,500** (CS101 = Rs 12,000, AI202 = Rs 18,000, late fee = Rs 500). | Y |  |
| 5 | search_handbook | I don't know. | Y |  |
