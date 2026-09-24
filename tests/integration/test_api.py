import socket
import threading
import time
from collections.abc import Iterator

import httpx
import pytest
import uvicorn

from contabilidad.api import EstadoContable, crear_api

pytestmark = pytest.mark.integration


def puerto_disponible() -> int:
    with socket.socket() as socket_temporal:
        socket_temporal.bind(("127.0.0.1", 0))
        return int(socket_temporal.getsockname()[1])


@pytest.fixture
def cliente() -> Iterator[httpx.Client]:
    puerto = puerto_disponible()
    configuracion = uvicorn.Config(
        crear_api(EstadoContable()),
        host="127.0.0.1",
        port=puerto,
        log_level="error",
    )
    servidor = uvicorn.Server(configuracion)
    hilo = threading.Thread(target=servidor.run, daemon=True)
    hilo.start()
    url_base = f"http://127.0.0.1:{puerto}"

    for _ in range(50):
        try:
            respuesta = httpx.get(f"{url_base}/api/salud", timeout=0.2)
            if respuesta.status_code == 200:
                break
        except httpx.TransportError:
            time.sleep(0.05)
    else:
        servidor.should_exit = True
        hilo.join(timeout=5)
        pytest.fail("La API no estuvo disponible dentro del tiempo esperado.")

    try:
        with httpx.Client(base_url=url_base) as cliente_aislado:
            yield cliente_aislado
    finally:
        servidor.should_exit = True
        hilo.join(timeout=5)
        if hilo.is_alive():
            pytest.fail("El servidor de integración no se cerró correctamente.")


def test_api_registra_movimientos_y_expone_resumen(
    cliente: httpx.Client,
) -> None:
    ingreso = cliente.post(
        "/api/movimientos",
        json={"tipo": "ingreso", "monto": "1500"},
    )
    egreso = cliente.post(
        "/api/movimientos",
        json={"tipo": "egreso", "monto": "400"},
    )
    resumen = cliente.get("/api/resumen")

    assert ingreso.status_code == 201
    assert ingreso.json() == {"numero": 1, "tipo": "ingreso", "monto": "1500"}
    assert egreso.status_code == 201
    assert resumen.status_code == 200
    assert resumen.json() == {
        "ingresos": "1500",
        "egresos": "400",
        "saldo": "1100",
        "clasificacion": "SUPERAVIT",
    }


def test_api_rechaza_movimiento_con_monto_cero(cliente: httpx.Client) -> None:
    respuesta = cliente.post(
        "/api/movimientos",
        json={"tipo": "ingreso", "monto": "0"},
    )

    assert respuesta.status_code == 422
    assert respuesta.json()["detail"] == "El monto debe ser mayor que cero."


def test_api_rechaza_asiento_descuadrado_con_conflicto(
    cliente: httpx.Client,
) -> None:
    respuesta = cliente.post(
        "/api/asientos",
        json={"debe": "100", "haber": "90"},
    )

    assert respuesta.status_code == 409
    assert respuesta.json()["detail"] == (
        "El asiento no puede registrarse: Debe y Haber no coinciden."
    )


@pytest.mark.parametrize(
    ("fecha_vencimiento", "pagada", "vencida"),
    [
        ("2026-09-22", False, True),
        ("2026-09-23", False, False),
        ("2026-09-22", True, False),
    ],
)
def test_api_evalua_cuenta_segun_contrato(
    cliente: httpx.Client,
    fecha_vencimiento: str,
    pagada: bool,
    vencida: bool,
) -> None:
    respuesta = cliente.post(
        "/api/cuentas/evaluar",
        json={
            "fecha_vencimiento": fecha_vencimiento,
            "fecha_evaluacion": "2026-09-23",
            "pagada": pagada,
        },
    )

    assert respuesta.status_code == 200
    assert respuesta.json() == {"vencida": vencida}
