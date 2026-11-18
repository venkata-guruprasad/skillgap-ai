"""Standalone script to verify PostgreSQL connectivity via SQLAlchemy settings."""

import sys
from pathlib import Path

# Add backend directory to sys.path so app modules can be imported cleanly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.database import check_db_connection  # noqa: E402


def main() -> int:
    ok, message = check_db_connection()
    print(f"[DB CHECK] {'SUCCESS' if ok else 'FAILED'}: {message}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
