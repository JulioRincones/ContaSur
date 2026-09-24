"""API consumible para integrar las reglas contables."""

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Literal

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

from contabilidad.negocio import (
    CuentaPorPagar,
    Movimiento,
    MovimientoTipo,
    clasificar_saldo,
    cuenta_esta_vencida,
    registrar_asiento,
    registrar_movimiento,
    saldo_contable,
)


class MovimientoEntrada(BaseModel):
    tipo: MovimientoTipo
    monto: Decimal


class MovimientoRespuesta(MovimientoEntrada):
    numero: int


class ResumenRespuesta(BaseModel):
    ingresos: Decimal
    egresos: Decimal
    saldo: Decimal
    clasificacion: Literal["SUPERAVIT", "EQUILIBRIO", "DEFICIT"]


class AsientoEntrada(BaseModel):
    debe: Decimal
    haber: Decimal


class AsientoRespuesta(AsientoEntrada):
    estado: Literal["CUADRADO"]


class CuentaEntrada(BaseModel):
    fecha_vencimiento: date
    fecha_evaluacion: date
    pagada: bool = False


class CuentaRespuesta(BaseModel):
    vencida: bool


@dataclass
class EstadoContable:
    movimientos: list[Movimiento] = field(default_factory=list)


def crear_api(estado: EstadoContable | None = None) -> FastAPI:
    """Crea una API con estado aislable para producción y pruebas."""

    api = FastAPI(title="ContaSur API", version="0.2.0")
    estado_actual = estado if estado is not None else EstadoContable()

    @api.get("/api/salud")
    def salud() -> dict[str, str]:
        return {"estado": "ok"}

    @api.post(
        "/api/movimientos",
        response_model=MovimientoRespuesta,
        status_code=status.HTTP_201_CREATED,
    )
    def crear_movimiento(datos: MovimientoEntrada) -> MovimientoRespuesta:
        try:
            movimiento = registrar_movimiento(datos.tipo, datos.monto)
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error

        estado_actual.movimientos.append(movimiento)
        return MovimientoRespuesta(
            numero=len(estado_actual.movimientos),
            tipo=movimiento.tipo,
            monto=movimiento.monto,
        )

    @api.get("/api/resumen", response_model=ResumenRespuesta)
    def obtener_resumen() -> ResumenRespuesta:
        ingresos = sum(
            (
                movimiento.monto
                for movimiento in estado_actual.movimientos
                if movimiento.tipo == "ingreso"
            ),
            Decimal("0"),
        )
        egresos = sum(
            (
                movimiento.monto
                for movimiento in estado_actual.movimientos
                if movimiento.tipo == "egreso"
            ),
            Decimal("0"),
        )
        saldo = saldo_contable(estado_actual.movimientos)
        return ResumenRespuesta(
            ingresos=ingresos,
            egresos=egresos,
            saldo=saldo,
            clasificacion=clasificar_saldo(saldo),
        )

    @api.post(
        "/api/asientos",
        response_model=AsientoRespuesta,
        status_code=status.HTTP_201_CREATED,
    )
    def crear_asiento(datos: AsientoEntrada) -> AsientoRespuesta:
        try:
            asiento = registrar_asiento(datos.debe, datos.haber)
        except ValueError as error:
            raise HTTPException(status_code=409, detail=str(error)) from error

        return AsientoRespuesta(
            debe=asiento.debe,
            haber=asiento.haber,
            estado="CUADRADO",
        )

    @api.post("/api/cuentas/evaluar", response_model=CuentaRespuesta)
    def evaluar_cuenta(datos: CuentaEntrada) -> CuentaRespuesta:
        cuenta = CuentaPorPagar(
            fecha_vencimiento=datos.fecha_vencimiento,
            pagada=datos.pagada,
        )
        return CuentaRespuesta(
            vencida=cuenta_esta_vencida(cuenta, datos.fecha_evaluacion)
        )

    return api


app = crear_api()
