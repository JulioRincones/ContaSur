import os
import subprocess
import sys
from pathlib import Path


def test_regresion_paquete_disponible_fuera_del_directorio_del_proyecto(
    tmp_path: Path,
) -> None:
    entorno = os.environ.copy()
    entorno.pop("PYTHONPATH", None)

    resultado = subprocess.run(
        [sys.executable, "-c", "import contabilidad"],
        cwd=tmp_path,
        env=entorno,
        capture_output=True,
        text=True,
        check=False,
    )

    assert resultado.returncode == 0, resultado.stderr
