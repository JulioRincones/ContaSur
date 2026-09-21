from datetime import date
from decimal import Decimal

import pytest

from contabilidad import (
    AsientoContable,
    CuentaPorPagar,
    clasificar_saldo,
    cuenta_esta_vencida,
    registrar_movimiento,
    saldo_contable,
)


def test_rn_01_rechaza_montos_iguales_o_inferiores_a_cero() -> None:
    with pytest.raises(ValueError, match="mayor que cero"):
        registrar_movimiento("ingreso", Decimal("0"))

    with pytest.raises(ValueError, match="mayor que cero"):
        registrar_movimiento("egreso", Decimal("-1"))


def test_rn_01_registra_movimientos_con_monto_mayor_que_cero() -> None:
    movimiento = registrar_movimiento("ingreso", Decimal("1"))

    assert movimiento.monto == Decimal("1")
    assert movimiento.tipo == "ingreso"


def test_rn_02_calcula_saldo_como_ingresos_menos_egresos() -> None:
    movimientos = [
        registrar_movimiento("ingreso", Decimal("1500")),
        registrar_movimiento("ingreso", Decimal("250")),
        registrar_movimiento("egreso", Decimal("400")),
    ]

    assert saldo_contable(movimientos) == Decimal("1350")


def test_rn_03_detecta_asiento_cuadrado_y_descuadrado() -> None:
    asiento_cuadrado = AsientoContable(debe=Decimal("900"), haber=Decimal("900"))
    asiento_descuadrado = AsientoContable(debe=Decimal("900"), haber=Decimal("899.99"))

    assert asiento_cuadrado.esta_cuadrado is True
    assert asiento_descuadrado.esta_cuadrado is False


def test_rn_04_detecta_cuentas_vencidas_segun_fecha_y_pago() -> None:
    fecha_evaluacion = date(2026, 9, 8)
    cuenta_impaga_vencida = CuentaPorPagar(date(2026, 9, 7), pagada=False)
    cuenta_impaga_no_vencida = CuentaPorPagar(date(2026, 9, 8), pagada=False)
    cuenta_pagada_vencida = CuentaPorPagar(date(2026, 9, 7), pagada=True)

    assert cuenta_esta_vencida(cuenta_impaga_vencida, fecha_evaluacion) is True
    assert cuenta_esta_vencida(cuenta_impaga_no_vencida, fecha_evaluacion) is False
    assert cuenta_esta_vencida(cuenta_pagada_vencida, fecha_evaluacion) is False


@pytest.mark.parametrize(
    ("saldo", "clasificacion"),
    [
        (Decimal("1"), "SUPERAVIT"),
        (Decimal("0"), "EQUILIBRIO"),
        (Decimal("-1"), "DEFICIT"),
    ],
)
def test_rn_05_clasifica_superavit_equilibrio_y_deficit(
    saldo: Decimal,
    clasificacion: str,
) -> None:
    assert clasificar_saldo(saldo) == clasificacion
