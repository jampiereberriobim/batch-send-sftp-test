import json
import sys

from src.entrypoints.lambda_handler import lambda_handler


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: python -m src.entrypoints.batch_handler '<event-json>'"
        )

    try:
        event = json.loads(sys.argv[1])
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid event JSON: {exc}") from exc

    if not isinstance(event, dict):
        raise SystemExit("The execution event must be a JSON object.")

    response = lambda_handler(event, None)
    print(json.dumps(response, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
