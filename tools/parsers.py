# tools/parsers.py
from __future__ import annotations
import re
import uuid
from typing import List, Dict


def parse_tasks_from_text(text: str, source: str = "unknown") -> List[Dict]:
    """
    Parse plain-text bullet lists (from LLM) into structured tasks.
    - Splits on newlines / bullets
    - Assigns unique IDs
    - Sets default confidence=0.8
    """
    tasks: List[Dict] = []
    lines = text.strip().splitlines()

    for line in lines:
        # Strip bullets/numbers
        clean = re.sub(r"^[\-\*\d\.\)\s]+", "", line).strip()
        if not clean:
            continue

        tasks.append(
            {
                "id": str(uuid.uuid4()),
                "title": clean,
                "source": source,
                "priority": "MED",
                "due": None,
                "estimate_min": None,
                "status": "PENDING",
                "confidence": 0.8,
            }
        )

    return tasks
