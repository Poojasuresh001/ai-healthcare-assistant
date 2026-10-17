"""Check the local Python version and virtual-environment activation."""

import sys


def main() -> int:
    """Print environment diagnostics and return a useful process status."""
    print(f"Python: {sys.version.split()[0]}")

    if sys.version_info < (3, 11) or sys.version_info >= (3, 13):
        print("ERROR: Use Python 3.11 or 3.12 for this project.")
        return 1

    in_virtual_environment = sys.prefix != sys.base_prefix
    if not in_virtual_environment:
        print("ERROR: No virtual environment is active.")
        print("Activate .venv, or run this with .venv\\Scripts\\python.exe.")
        return 1

    print("Virtual environment: active")
    print("Phase 1 check: passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
