from decimal import Decimal
from time import perf_counter

import pytest

from contabilidad import Movimiento, saldo_contable

pytestmark = pytest.mark.nonfunctional

CANTIDAD_MOVIMIENTOS = 10_000
UMBRAL_SEGUNDOS = 0.5


def test_rendimiento_calcula_diez_mil_movimientos_en_medio_segundo() -> None:
    movimientos = [
        Movimiento(
            tipo="ingreso" if indice % 2 == 0 else "egreso",
            monto=Decimal("100"),
        )
        for indice in range(CANTIDAD_MOVIMIENTOS)
    ]

    inicio = perf_counter()
    saldo = saldo_contable(movimientos)
    duracion = perf_counter() - inicio

    assert saldo == Decimal("0")
    assert duracion < UMBRAL_SEGUNDOS, (
        f"El cálculo tardó {duracion:.6f}s; umbral: {UMBRAL_SEGUNDOS:.1f}s"
    )
    print(f"rendimiento_saldo_segundos={duracion:.6f}")
