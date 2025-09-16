# tests/test_pipeline.py
from orchestration.graph import build_graph
from datetime import datetime

if __name__ == "__main__":
    DOC_ID = "1Db_gPHiLzFE1HO4dBXB2RpLrdxTV8iAJAXF4RbaJekw"

    workflow = build_graph(DOC_ID)
    result: dict = workflow.invoke({})  # start with empty dict

    print("=== Welcome to your personal productivity planning assistant ===")
    print("=== Here is your day at a glance ===")

    # --- Summaries ---
    print("\n=== Email Summaries ===")
    for s in result.get("summaries", []):
        print(f"- [{s.category}] {s.subject}: {s.text}")

    # --- Tasks by Priority ---
    print("\n=== Tasks by Priority ===")
    grouped = {"HIGH": [], "MED": [], "LOW": []}
    for t in result["tasks"]:
        grouped[t.priority].append(t)

    for level in ["HIGH", "MED", "LOW"]:
        print(f"\n[{level}]")
        if not grouped[level]:
            print("(none)")
        for t in grouped[level]:
            print(f"- {t.title} (due={t.due_date}, conf={t.confidence:.2f})")

    # --- Proposed Time Blocks ---
    print("\n=== Proposed Time Blocks ===")
    for b in result["proposals"]:
        print("-", b.convert_readable())


    log_file = "pipeline_logs.txt"
    with open(log_file, "a", encoding="utf-8") as f:  # append mode so old runs aren’t erased
        f.write(f"\n=== Run at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
        for log in result["logs"]:
            f.write(log + "\n")
    print("\nLogs saved to pipeline_logs.txt")

