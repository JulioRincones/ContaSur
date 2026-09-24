import socket
import subprocess
import sys
import time
from collections.abc import Iterator
from pathlib import Path
from urllib.request import urlopen

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.e2e

RAIZ_PROYECTO = Path(__file__).resolve().parents[2]


def puerto_disponible() -> int:
    with socket.socket() as socket_temporal:
        socket_temporal.bind(("127.0.0.1", 0))
        return int(socket_temporal.getsockname()[1])


def detener_proceso(proceso: subprocess.Popen[bytes]) -> None:
    if proceso.poll() is not None:
        return
    if sys.platform == "win32":
        subprocess.run(
            ["taskkill", "/PID", str(proceso.pid), "/T", "/F"],
            capture_output=True,
            check=False,
        )
        return

    proceso.terminate()
    try:
        proceso.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proceso.kill()
        proceso.wait(timeout=5)


@pytest.fixture(scope="session")
def servidor_streamlit() -> Iterator[str]:
    puerto = puerto_disponible()
    proceso = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "app.py",
            "--server.headless=true",
            f"--server.port={puerto}",
            "--browser.gatherUsageStats=false",
        ],
        cwd=RAIZ_PROYECTO,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )
    url_base = f"http://127.0.0.1:{puerto}"

    try:
        for _ in range(60):
            if proceso.poll() is not None:
                pytest.fail("Streamlit termino antes de iniciar el flujo E2E.")
            try:
                with urlopen(f"{url_base}/_stcore/health", timeout=1) as respuesta:
                    if respuesta.status == 200:
                        break
            except OSError:
                time.sleep(0.25)
        else:
            pytest.fail("Streamlit no estuvo disponible dentro del tiempo esperado.")

        yield url_base
    finally:
        detener_proceso(proceso)


def test_flujo_registra_ingreso_y_rechaza_asiento_descuadrado(
    page: Page,
    servidor_streamlit: str,
) -> None:
    page.goto(servidor_streamlit)

    expect(page.get_by_role("heading", name="ContaSur")).to_be_visible()
    page.get_by_label("Monto").fill("150000")
    page.get_by_role("button", name="Registrar movimiento").click()

    expect(page.get_by_text("Movimiento registrado correctamente.")).to_be_visible()
    expect(page.get_by_alt_text("Running...")).to_be_hidden(timeout=10_000)
    expect(page.get_by_text("$150.000", exact=True).first).to_be_visible()

    page.get_by_label("Debe").fill("100")
    page.get_by_label("Haber").fill("90")
    page.get_by_role("button", name="Registrar asiento").click()

    expect(
        page.get_by_text(
            "El asiento no puede registrarse: Debe y Haber no coinciden."
        )
    ).to_be_visible()
