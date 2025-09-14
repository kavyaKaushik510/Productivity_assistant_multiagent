# tests/test_parsers.py
from tools.parsers import parse_tasks_from_text


def test_parse_tasks_from_text():
    text = """
    - Send project report
    - Schedule review meeting
    * Confirm training date
    """
    tasks = parse_tasks_from_text(text, source="email")
    assert isinstance(tasks, list)
    assert len(tasks) == 3
    assert "title" in tasks[0]
    assert tasks[0]["source"] == "email"


if __name__ == "__main__":
    sample = """
    1. Finalize budget
    2. Update slides
    3) Email stakeholders
    """
    parsed = parse_tasks_from_text(sample, source="meeting")
    print("Parsed tasks:")
    for t in parsed:
        print(f"- {t['id'][:8]} | {t['title']} | {t['source']} | conf={t['confidence']}")
