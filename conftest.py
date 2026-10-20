import sys
from pathlib import Path

# Garante que a raiz do projeto esteja no sys.path para pytest
raiz = Path(__file__).resolve().parent
if str(raiz) not in sys.path:
    sys.path.insert(0, str(raiz))
