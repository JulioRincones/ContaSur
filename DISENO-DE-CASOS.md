# Diseño de casos de prueba

## 1. Convenciones

Los casos se derivan de las cinco reglas declaradas en `README.md`. Para los
montos se usa una precisión operativa de un centavo; por eso los valores
adyacentes a cero son `-0.01` y `0.01`. Las fechas se comparan por día, de modo
que los valores adyacentes son el día anterior y el día siguiente.

Cada caso tiene un identificador estable:

- `CU`: caso unitario.
- `CI`: caso de integración sobre la API.
- `CE`: caso extremo a extremo sobre Streamlit.

## 2. RN-01: validación de montos

### Particiones y límites

| Partición | Datos | Resultado |
|---|---|---|
| P1: monto negativo | `monto < 0` | Rechazo |
| P2: monto cero | `monto = 0` | Rechazo |
| P3: monto positivo | `monto > 0` | Movimiento válido |

El límite es `0`. Se prueban `-1`, `0` y `1`; los enteros hacen visible la
condición sin depender del formato decimal.

| Caso | Partición/límite | Resultado esperado | Prueba |
|---|---|---|---|
| CU-RN01-01 | P1, `-1` | `ValueError` | `test_rn_01_rechaza_montos_iguales_o_inferiores_a_cero` |
| CU-RN01-02 | P2, `0` | `ValueError` | `test_rn_01_rechaza_montos_iguales_o_inferiores_a_cero` |
| CU-RN01-03 | P3, `1` | Movimiento de ingreso | `test_rn_01_registra_movimientos_con_monto_mayor_que_cero` |
| CI-RN01-01 | Contrato HTTP, `0` | HTTP 422 y detalle de negocio | `test_api_rechaza_movimiento_con_monto_cero` |

## 3. RN-02: cálculo del saldo

### Particiones

La regla depende de la composición de la colección, no de un límite monetario.

| Partición | Composición | Resultado |
|---|---|---|
| P1 | Sin movimientos | Saldo `0` |
| P2 | Solo ingresos | Suma positiva |
| P3 | Solo egresos | Suma negativa |
| P4 | Ingresos y egresos | Ingresos menos egresos |

El límite estructural es la cantidad de movimientos: `0`, `1` y varios.

| Caso | Partición | Resultado esperado | Prueba |
|---|---|---|---|
| CU-RN02-01 | P1 | `0` | `test_rn_02_calcula_saldo_para_particiones_basicas` |
| CU-RN02-02 | P2 | `100` | `test_rn_02_calcula_saldo_para_particiones_basicas` |
| CU-RN02-03 | P3 | `-40` | `test_rn_02_calcula_saldo_para_particiones_basicas` |
| CU-RN02-04 | P4 | `1350` | `test_rn_02_calcula_saldo_como_ingresos_menos_egresos` |
| CI-RN02-01 | P4 vía API | HTTP 201 y resumen `1100` | `test_api_registra_movimientos_y_expone_resumen` |

## 4. RN-03: equilibrio de un asiento

### Particiones y límites

Se usa `diferencia = Debe - Haber`.

| Partición | Diferencia | Clasificación |
|---|---|---|
| P1 | `< 0` | Descuadrado |
| P2 | `= 0` | Cuadrado |
| P3 | `> 0` | Descuadrado |

Alrededor de cero se prueban `-0.01`, `0` y `0.01`.

### Tabla de decisión

| Debe = Haber | Intento de registro | Resultado |
|---|---|---|
| Sí | Sí | Aceptar asiento |
| No | Sí | Rechazar con error |

| Caso | Partición/decisión | Resultado esperado | Prueba |
|---|---|---|---|
| CU-RN03-01 | P1 | `esta_cuadrado = False` | `test_rn_03_detecta_asiento_cuadrado_y_descuadrado` |
| CU-RN03-02 | P2 | `esta_cuadrado = True` | `test_rn_03_detecta_asiento_cuadrado_y_descuadrado` |
| CU-RN03-03 | P3 | `esta_cuadrado = False` | `test_rn_03_detecta_asiento_cuadrado_y_descuadrado` |
| CU-RN03-04 | Descuadrado al registrar | `ValueError` | `test_rn_03_rechaza_registro_de_asiento_descuadrado` |
| CI-RN03-01 | Descuadrado vía API | HTTP 409 | `test_api_rechaza_asiento_descuadrado_con_conflicto` |
| CE-RN03-01 | Descuadrado desde UI | Mensaje visible de rechazo | `test_flujo_registra_ingreso_y_rechaza_asiento_descuadrado` |

## 5. RN-04: cuenta por pagar vencida

### Particiones, límites y tabla de decisión

La relación temporal tiene tres particiones: anterior, igual y posterior a la
fecha de evaluación. El pago domina la decisión: una cuenta pagada no está
vencida cualquiera sea su fecha.

| Pagada | Vencimiento respecto de evaluación | Vencida |
|---|---|---|
| Sí | Cualquiera | No |
| No | Anterior | Sí |
| No | Igual | No |
| No | Posterior | No |

Para una evaluación `2026-09-08`, los límites son `2026-09-07`, `2026-09-08`
y `2026-09-09`.

| Caso | Decisión | Resultado esperado | Prueba |
|---|---|---|---|
| CU-RN04-01 | Impaga/anterior | `True` | `test_rn_04_detecta_cuentas_vencidas_segun_fecha_y_pago` |
| CU-RN04-02 | Impaga/igual | `False` | `test_rn_04_detecta_cuentas_vencidas_segun_fecha_y_pago` |
| CU-RN04-03 | Impaga/posterior | `False` | `test_rn_04_detecta_cuentas_vencidas_segun_fecha_y_pago` |
| CU-RN04-04 | Pagada/anterior | `False` | `test_rn_04_detecta_cuentas_vencidas_segun_fecha_y_pago` |
| CI-RN04-01..03 | Contrato API: anterior, igual y pagada | JSON `vencida` correcto | `test_api_evalua_cuenta_segun_contrato` |

## 6. RN-05: clasificación del saldo

### Particiones y límites

| Partición | Saldo | Clasificación |
|---|---|---|
| P1 | `< 0` | `DEFICIT` |
| P2 | `= 0` | `EQUILIBRIO` |
| P3 | `> 0` | `SUPERAVIT` |

El límite es cero y se prueba con `-0.01`, `0` y `0.01`.

| Caso | Partición/límite | Resultado esperado | Prueba |
|---|---|---|---|
| CU-RN05-01 | P1, `-0.01` | `DEFICIT` | `test_rn_05_clasifica_superavit_equilibrio_y_deficit` |
| CU-RN05-02 | P2, `0` | `EQUILIBRIO` | `test_rn_05_clasifica_superavit_equilibrio_y_deficit` |
| CU-RN05-03 | P3, `0.01` | `SUPERAVIT` | `test_rn_05_clasifica_superavit_equilibrio_y_deficit` |

## 7. Flujo E2E

| Caso | Recorrido | Riesgo que detecta | Prueba |
|---|---|---|---|
| CE-FLUJO-01 | Abrir ContaSur, registrar ingreso, observar saldo, intentar asiento descuadrado | Controles ausentes, sesión que no actualiza el resumen o rechazo no visible | `test_flujo_registra_ingreso_y_rechaza_asiento_descuadrado` |

Este caso no repite todas las combinaciones unitarias. Su objetivo es verificar
que una persona pueda completar el recorrido y observar los resultados a través
del navegador.

## 8. Casos descartados

| Propuesta | Decisión | Justificación |
|---|---|---|
| Probar que una cuenta impaga con vencimiento igual a la evaluación está vencida | Descartada | Contradice RN-04, que exige fecha estrictamente anterior. Sería otra regla, no una ampliación válida. |
| Repetir todas las particiones de las cinco reglas en Playwright | Descartada | Duplicaría las unitarias y haría lenta y frágil la capa E2E sin cubrir otro riesgo. |
| Usar nombres, RUT o facturas reales | Descartada | Las reglas no necesitan identidad personal; viola minimización y no aporta cobertura. |
| Probar montos máximos arbitrarios | Descartada | El dominio no declara un máximo. Elegir uno inventaría un límite inexistente. |

## 9. Auditoría de casos propuestos por el agente

El agente propuso ampliar RN-04 con el caso "vence hoy = vencida", replicar las
cinco reglas completas en Playwright y usar un proveedor con datos realistas.
Julio auditó esas propuestas contra las reglas y el principio de minimización:

- Se rechazó "vence hoy = vencida" porque RN-04 usa comparación estricta.
- Se rechazó duplicar toda la suite en E2E; se conservó un recorrido vertical.
- Se rechazaron datos identificables y se reemplazaron por fechas y montos
  sintéticos.
- Se aceptaron las tres particiones temporales de RN-04, el límite de un centavo
  en RN-03/RN-05 y el flujo que combina movimiento y rechazo de asiento.

La decisión conserva casos derivados de técnicas formales y descarta volumen
sin fundamento. La evidencia queda en este documento, en las pruebas asociadas
y en el commit que incorpore la EP2.
