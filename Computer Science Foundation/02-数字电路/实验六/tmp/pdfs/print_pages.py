import json
import sys
from pathlib import Path


def main() -> None:
    path = Path(__file__).with_name("extracted_text.json")
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    end = int(sys.argv[2]) if len(sys.argv) > 2 else start
    data = json.loads(path.read_text(encoding="utf-8"))
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    for item in data[start - 1:end]:
        print(f"--- PAGE {item['page']} ---")
        print(item["text"])
        print()


if __name__ == "__main__":
    main()
