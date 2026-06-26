# Conftest: make `lib` importable as a top-level package during tests.
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
