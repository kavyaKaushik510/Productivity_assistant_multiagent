# tests/test_pipeline_graph.py
from orchestration.graph import build_graph
from orchestration.state import PlannerState

if __name__ == "__main__":
    DOC_ID = "1Db_gPHiLzFE1HO4dBXB2RpLrdxTV8iAJAXF4RbaJekw"  # replace with a real Google Doc ID

    workflow = build_graph(DOC_ID)
    result: PlannerState = workflow.invoke(PlannerState())

    print("=== PIPELINE (LangGraph) DEMO ===")

    print("\n=== Tasks by Priority ===")
    grouped = {"HIGH": [], "MED": [], "LOW": []}
    for t in result.tasks:
        grouped[t.priority].append(t)

    for level in ["HIGH", "MED", "LOW"]:
        print(f"\n[{level}]")
        if not grouped[level]:
            print("(none)")
        for t in grouped[level]:
            print(f"- {t.title} (due={t.due_date}, conf={t.confidence:.2f})")

    print("\n=== Proposed Time Blocks ===")
    for b in result.proposals:
        print("-", b.convert_readable())

    print("\n=== Logs ===")
    for log in result.logs:
        print("-", log)
