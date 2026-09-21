"""Reglas contables observables del sistema."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Literal

MovimientoTipo = Literal["ingreso", "egreso"]
ClasificacionSaldo = Literal["SUPERAVIT", "EQUILIBRIO", "DEFICIT"]


@dataclass(frozen=True)
class Movimiento:
    """Movimiento contable de ingreso o egreso."""

    tipo: MovimientoTipo
    monto: Decimal

    def __post_init__(self) -> None:
        validar_monto(self.monto)


@dataclass(frozen=True)
class AsientoContable:
    """Totales de Debe y Haber de un asiento contable."""

    debe: Decimal
    haber: Decimal

    @property
    def esta_cuadrado(self) -> bool:
        return self.debe == self.haber


def registrar_asiento(debe: Decimal, haber: Decimal) -> AsientoContable:
    """Rechaza un asiento si sus totales Debe y Haber no coinciden."""

    asiento = AsientoContable(debe=debe, haber=haber)
    if not asiento.esta_cuadrado:
        raise ValueError("El asiento no puede registrarse: Debe y Haber no coinciden.")
    return asiento


@dataclass(frozen=True)
class CuentaPorPagar:
    """Documento por pagar evaluable segun vencimiento y estado de pago."""

    fecha_vencimiento: date
    pagada: bool = False

    def esta_vencida(self, fecha_evaluacion: date) -> bool:
        return cuenta_esta_vencida(self, fecha_evaluacion)


def validar_monto(monto: Decimal) -> None:
    """Rechaza montos contables iguales o inferiores a cero."""

    if monto <= Decimal("0"):
        raise ValueError("El monto debe ser mayor que cero.")


def registrar_movimiento(tipo: MovimientoTipo, monto: Decimal) -> Movimiento:
    """Crea un movimiento valido de ingreso o egreso."""

    return Movimiento(tipo=tipo, monto=monto)


def saldo_contable(movimientos: list[Movimiento]) -> Decimal:
    """Calcula saldo como total de ingresos menos total de egresos."""

    ingresos = sum(
        (
            movimiento.monto
            for movimiento in movimientos
            if movimiento.tipo == "ingreso"
        ),
        Decimal("0"),
    )
    egresos = sum(
        (
            movimiento.monto
            for movimiento in movimientos
            if movimiento.tipo == "egreso"
        ),
        Decimal("0"),
    )
    return ingresos - egresos


def cuenta_esta_vencida(
    cuenta: CuentaPorPagar,
    fecha_evaluacion: date,
) -> bool:
    """Indica si una cuenta impaga vencio antes de la fecha evaluada."""

    return not cuenta.pagada and cuenta.fecha_vencimiento < fecha_evaluacion


def clasificar_saldo(saldo: Decimal) -> ClasificacionSaldo:
    """Clasifica un saldo en SUPERAVIT, EQUILIBRIO o DEFICIT."""

    if saldo > Decimal("0"):
        return "SUPERAVIT"
    if saldo == Decimal("0"):
        return "EQUILIBRIO"
    return "DEFICIT"
