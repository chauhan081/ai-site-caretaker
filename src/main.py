from pathlib import Path


def main() -> int:
    print("AI Site Caretaker scaffold initialized")
    print(f"Project root: {Path(__file__).resolve().parent.parent}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
