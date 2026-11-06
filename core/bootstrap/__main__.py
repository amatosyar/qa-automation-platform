"""CLI del Bootstrap."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from core.bootstrap import bootstrap_project


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Crear proyecto consumidor "
            "QA Automation Platform."
        )
    )

    parser.add_argument(
        "--project",
        required=True,
    )

    parser.add_argument(
        "--matrix",
        required=True,
    )

    parser.add_argument(
        "--ef",
        required=True,
    )

    parser.add_argument(
        "--et",
        required=True,
    )

    parser.add_argument(
        "--force",
        action="store_true",
    )

    args = parser.parse_args()

    result = bootstrap_project(
        project_root=Path(args.project),
        matrix=Path(args.matrix),
        ef=Path(args.ef),
        et=Path(args.et),
        force=args.force,
    )

    print(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
