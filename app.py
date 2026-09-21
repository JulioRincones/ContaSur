from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any

import streamlit as st

from contabilidad import (
    AsientoContable,
    CuentaPorPagar,
    Movimiento,
    MovimientoTipo,
    clasificar_saldo,
    cuenta_esta_vencida,
    registrar_movimiento,
    saldo_contable,
)


def decimal_desde_texto(valor: str) -> Decimal:
    texto_limpio = valor.strip().replace(",", ".")
    if not texto_limpio:
        raise ValueError("Ingresa un monto.")

    try:
        return Decimal(texto_limpio)
    except InvalidOperation as error:
        raise ValueError("Ingresa un numero valido.") from error


def formato_pesos(valor: Decimal) -> str:
    return f"${valor:,.0f}".replace(",", ".")


def movimientos_guardados() -> list[Movimiento]:
    if "movimientos" not in st.session_state:
        st.session_state.movimientos = []
    return st.session_state.movimientos


def agregar_estilos() -> None:
    st.markdown(
        """
        <style>
        .main .block-container {
            padding-top: 2rem;
            max-width: 1180px;
        }

        [data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 16px 18px;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
        }

        .estado {
            border-radius: 8px;
            padding: 14px 16px;
            border: 1px solid #d1d5db;
            background: #f9fafb;
            font-weight: 600;
        }

        .estado.ok {
            border-color: #86efac;
            background: #f0fdf4;
            color: #166534;
        }

        .estado.warn {
            border-color: #fde68a;
            background: #fffbeb;
            color: #92400e;
        }

        .estado.bad {
            border-color: #fecaca;
            background: #fef2f2;
            color: #991b1b;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def mostrar_estado(texto: str, clase: str) -> None:
    st.markdown(
        f'<div class="estado {clase}">{texto}</div>',
        unsafe_allow_html=True,
    )


def registrar_movimiento_ui() -> None:
    st.subheader("Registrar movimiento")
    with st.form("form_movimiento", clear_on_submit=True):
        tipo_opcion = st.segmented_control(
            "Tipo",
            options=["Ingreso", "Egreso"],
            default="Ingreso",
        )
        monto_texto = st.text_input("Monto", placeholder="Ejemplo: 150000")
        enviado = st.form_submit_button("Registrar movimiento", type="primary")

    if not enviado:
        return

    tipo: MovimientoTipo = "ingreso" if tipo_opcion == "Ingreso" else "egreso"
    try:
        monto = decimal_desde_texto(monto_texto)
        movimiento = registrar_movimiento(tipo, monto)
    except ValueError as error:
        st.error(str(error))
        return

    movimientos_guardados().append(movimiento)
    st.success("Movimiento registrado correctamente.")


def resumen_contable_ui(movimientos: list[Movimiento]) -> None:
    total_ingresos = sum(
        (
            movimiento.monto
            for movimiento in movimientos
            if movimiento.tipo == "ingreso"
        ),
        Decimal("0"),
    )
    total_egresos = sum(
        (
            movimiento.monto
            for movimiento in movimientos
            if movimiento.tipo == "egreso"
        ),
        Decimal("0"),
    )
    saldo = saldo_contable(movimientos)
    clasificacion = clasificar_saldo(saldo)

    st.subheader("Resumen contable")
    col_ingresos, col_egresos, col_saldo = st.columns(3)
    col_ingresos.metric("Ingresos", formato_pesos(total_ingresos))
    col_egresos.metric("Egresos", formato_pesos(total_egresos))
    col_saldo.metric("Saldo", formato_pesos(saldo))

    clase = {
        "SUPERAVIT": "ok",
        "EQUILIBRIO": "warn",
        "DEFICIT": "bad",
    }[clasificacion]
    mostrar_estado(f"Situacion actual: {clasificacion}", clase)


def asiento_contable_ui() -> None:
    st.subheader("Asiento contable")
    col_debe, col_haber = st.columns(2)
    debe_texto = col_debe.text_input("Debe", value="0", key="debe")
    haber_texto = col_haber.text_input("Haber", value="0", key="haber")

    try:
        asiento = AsientoContable(
            debe=decimal_desde_texto(debe_texto),
            haber=decimal_desde_texto(haber_texto),
        )
    except ValueError as error:
        st.error(str(error))
        return

    if asiento.esta_cuadrado:
        mostrar_estado("Asiento cuadrado: Debe y Haber coinciden.", "ok")
    else:
        diferencia = asiento.debe - asiento.haber
        mostrar_estado(
            f"Asiento descuadrado. Diferencia: {formato_pesos(diferencia)}",
            "bad",
        )


def cuenta_por_pagar_ui() -> None:
    st.subheader("Cuenta por pagar")
    col_vencimiento, col_evaluacion = st.columns(2)
    vencimiento = col_vencimiento.date_input("Fecha de vencimiento", value=date.today())
    evaluacion = col_evaluacion.date_input("Fecha de evaluacion", value=date.today())
    pagada = st.checkbox("Pagada")

    cuenta = CuentaPorPagar(fecha_vencimiento=vencimiento, pagada=pagada)
    vencida = cuenta_esta_vencida(cuenta, evaluacion)

    if vencida:
        mostrar_estado("Cuenta vencida.", "bad")
    elif pagada:
        mostrar_estado("Cuenta pagada, no vencida.", "ok")
    else:
        mostrar_estado("Cuenta no vencida.", "warn")


def historial_ui(movimientos: list[Movimiento]) -> None:
    st.subheader("Historial")
    if not movimientos:
        st.info("Aun no hay movimientos registrados.")
        return

    filas: list[dict[str, Any]] = [
        {
            "N": indice,
            "Tipo": movimiento.tipo.capitalize(),
            "Monto": formato_pesos(movimiento.monto),
        }
        for indice, movimiento in enumerate(movimientos, start=1)
    ]
    st.dataframe(filas, hide_index=True, use_container_width=True)

    if st.button("Limpiar historial"):
        movimientos.clear()
        st.rerun()


def main() -> None:
    st.set_page_config(
        page_title="ContaSur",
        page_icon="CS",
        layout="wide",
    )
    agregar_estilos()

    st.title("ContaSur")
    st.caption("Panel contable simple para validar reglas de negocio.")

    movimientos = movimientos_guardados()

    resumen_contable_ui(movimientos)
    st.divider()

    col_registro, col_asiento = st.columns([1.05, 1])
    with col_registro:
        registrar_movimiento_ui()
    with col_asiento:
        asiento_contable_ui()

    st.divider()
    col_cuenta, col_historial = st.columns([1, 1.2])
    with col_cuenta:
        cuenta_por_pagar_ui()
    with col_historial:
        historial_ui(movimientos)


if __name__ == "__main__":
    main()
