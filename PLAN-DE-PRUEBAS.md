# Plan de pruebas de ContaSur

## 1. Identificación

Plan incremental para la Evaluación Parcial 2 de PRO402, basado en ISO/IEC/IEEE
29119. Mantiene la línea base de la EP1 y agrega diseño formal, integración y
pruebas extremo a extremo.

## 2. Alcance

### Incluido

- RN-01: validación de montos.
- RN-02: cálculo del saldo.
- RN-03: clasificación y rechazo de asientos descuadrados.
- RN-04: vencimiento según fecha y pago.
- RN-05: clasificación del saldo.
- Contratos HTTP de movimientos, resumen, asientos y cuentas.
- Flujo web de registro de ingreso y rechazo de asiento descuadrado.
- Rendimiento del cálculo de saldo, seguridad de entrada y accesibilidad de los
  controles críticos.
- Instalación del paquete y controles Ruff/Pyrefly.

### Excluido

- Persistencia en base de datos y concurrencia multiusuario.
- Autenticación, autorización y datos personales.
- Tributación, facturación electrónica y normativa contable externa.
- Carga concurrente, accesibilidad exhaustiva y múltiples navegadores.
- Despliegue productivo y recuperación ante desastres.

Estas exclusiones corresponden al alcance educativo actual y no se presentan
como comportamientos verificados.

## 3. Riesgos del producto

Probabilidad e impacto usan escala `1` (bajo), `2` (medio) y `3` (alto). La
exposición es `P x I`: `1-2` baja, `3-4` media y `6-9` alta. La probabilidad se
basa en la cantidad de condiciones, integraciones o defectos ya observados; el
impacto considera si impide operar o entrega un resultado contable incorrecto.

| Riesgo | P | I | Exposición | Fundamento | Calidad ISO 25010 | Respuesta de prueba |
|---|---:|---:|---:|---|---|---|
| R1: aceptar montos o asientos inválidos | 2 | 3 | 6 Alta | Tiene límites y un defecto previo de validación; aceptarlo altera registros | Adecuación funcional, fiabilidad | Límites unitarios, error HTTP y rechazo E2E |
| R2: calcular o clasificar mal el saldo | 2 | 3 | 6 Alta | Varias ramas alimentan el resultado principal | Adecuación funcional | Particiones unitarias, resumen y rendimiento |
| R3: contrato API incompatible | 2 | 2 | 4 Media | Campos y códigos pueden cambiar aunque el dominio siga correcto | Compatibilidad, fiabilidad | Estados HTTP y cuerpos exactos |
| R4: interfaz no actualiza estado o pierde el rechazo | 2 | 2 | 4 Media | Ya ocurrió un resumen visual desactualizado | Adecuación funcional, usabilidad | Recorrido Playwright y controles accesibles |
| R5: pruebas con estado compartido o intermitentes | 2 | 2 | 4 Media | Usa servidores, puertos y navegador | Fiabilidad, mantenibilidad | Estado aislado, puertos libres y cierre verificable |
| R6: exposición de datos personales | 1 | 2 | 2 Baja | El alcance no solicita datos personales | Seguridad | Datos sintéticos, campos extra prohibidos y minimización |
| R7: paquete no instalable fuera del repositorio | 1 | 3 | 3 Media | Ya ocurrió una vez; bloquearía toda ejecución | Portabilidad, mantenibilidad | Regresión de empaquetado y CI desde clon |

## 4. Estrategia por nivel

### Unitarias

Ejecutan funciones y objetos de `contabilidad.negocio` sin HTTP ni navegador.
Son el nivel adecuado para particiones, límites y tablas de decisión porque
localizan con precisión la regla rota y se ejecutan rápidamente.

### Integración

Levantan la aplicación FastAPI completa con Uvicorn en un puerto libre y envían
solicitudes HTTP reales. Verifican serialización, validación de entrada, códigos
HTTP, cuerpos de respuesta, enrutamiento y conexión con el dominio. Cada prueba
recibe un `EstadoContable` nuevo; no se simula la regla de negocio.

### Extremo a extremo

Levanta Streamlit en un puerto libre y Playwright usa Chromium para recorrer la
interfaz. Verifica elementos visibles, formularios, reruns, estado de sesión y
mensajes. No repite todas las combinaciones del dominio.

## 5. Trazabilidad

El detalle completo de particiones y valores está en `DISENO-DE-CASOS.md`.

| Riesgo | Requisito | Casos | Pruebas automatizadas | Resultado CI |
|---|---|---|---|---|
| R1 | RN-01 | CU-RN01-01..03, CI-RN01-01 | Pruebas RN-01 y `test_api_rechaza_movimiento_con_monto_cero` | Verde, ejecución 36364345551 |
| R1 | RN-03 | CU-RN03-01..04, CI-RN03-01..02, CE-RN03-01 | Pruebas RN-03, contratos de asiento y flujo Playwright | Verde, ejecución 36364345551 |
| R2 | RN-02/RN-05 | CU-RN02-01..04, CI-RN02-01, CU-RN05-01..03 | Pruebas de saldo, resumen, clasificación y rendimiento | Verde, ejecución 36364345551 |
| R3 | Contrato HTTP | CI-RN01-01, CI-RN02-01, CI-RN03-01, CI-RN04-01..03 | `tests/integration/test_api.py` | Rojo 36364212305; verde 36364345551 |
| R4 | Flujo web | CE-FLUJO-01 | `tests/e2e/test_streamlit.py` | Verde, ejecución 36364345551 |
| R5 | Aislamiento | Todos los CI/CE | Fixtures `cliente` y `servidor_streamlit` | Verde, ejecución 36364345551 |
| R6 | Protección de datos | Todos | Seguridad de entrada y literales sintéticos | Rojo 36364212305; verde 36364345551 |
| R7 | Ejecutabilidad | Regresión EP1 | `test_regresion_paquete_disponible_fuera_del_directorio_del_proyecto` | Verde, ejecución 36364345551 |

## 6. Datos de prueba

Todos los datos son sintéticos. No se usan nombres, RUT, correos, cuentas
bancarias, documentos ni archivos de producción.

| Nivel | Datos | Generación | Eliminación/aislamiento |
|---|---|---|---|
| Unitario | `Decimal`, fechas fijas y tipos ingreso/egreso | Literales en cada caso | Objetos en memoria descartados al terminar |
| Integración | JSON con montos y fechas fijas | Fixture y cuerpo de solicitud | `EstadoContable` nuevo por prueba |
| E2E | Ingreso `150000`, asiento `100/90` | Entrada de Playwright | Sesión termina al cerrar servidor Streamlit |

El principio de minimización se aplica usando solo los campos requeridos por
cada contrato. Las pruebas no escriben una base de datos ni generan capturas con
datos personales.

## 7. Preparación y dobles

- Pytest prepara objetos de dominio directamente en unitarias.
- La integración usa un repositorio en memoria (`EstadoContable`) inyectado a la
  fábrica `crear_api` y un servidor Uvicorn real; reemplaza futura persistencia,
  no la lógica contable.
- E2E usa la aplicación real, un servidor real y Chromium. No usa dobles.
- El puerto E2E se solicita al sistema para evitar colisiones.

## 8. Criterios de entrada

- Dependencias instaladas con `uv sync`.
- Chromium instalado con `uv run playwright install chromium`.
- Reglas RN-01 a RN-05 y contratos documentados.
- Ruff y Pyrefly sin errores.
- Datos sintéticos disponibles en las propias pruebas.

## 9. Criterios de salida

- Unitarias, integración y E2E terminan sin fallos.
- Ruff y Pyrefly terminan con código cero.
- Todo caso implementado tiene identificador y trazabilidad.
- Todo caso diseñado no implementado tiene justificación.
- No existen secretos ni datos personales reales.
- El servidor E2E se cierra y no deja datos persistentes.
- Cualquier inestabilidad conocida queda registrada; actualmente no se acepta
  una prueba intermitente como evidencia en verde.

## 10. Comandos de ejecución

```bash
uv run pytest tests/unit
uv run pytest tests/integration
uv run pytest tests/e2e
uv run pytest -m regression
uv run pytest -m nonfunctional
uv run pytest
uv run ruff check .
uv run pyrefly check
```

## 11. Responsabilidades y evidencia

Julio Rincones revisa las reglas, acepta o descarta los casos y entrega el
repositorio. El agente propone estructura, casos y automatización; sus propuestas
se auditan en `DISENO-DE-CASOS.md` y `README.md`. La salida de Pytest, Ruff,
Pyrefly y el historial Git constituyen la evidencia reproducible.

## 12. Regresión e inestabilidad

El marcador `regression` protege tres defectos corregidos:

- El paquete no estaba disponible al ejecutar Streamlit fuera del contexto de
  Pytest.
- Un asiento descuadrado podía detectarse sin impedir su registro.
- El resumen visual seguía mostrando `$0` después de registrar un ingreso.

No existen pruebas omitidas con `skip` ni fallos esperados con `xfail`. El E2E
mostró una espera incorrecta durante su construcción; se investigó el rerun de
Streamlit, se esperó el indicador de ejecución y se cerró explícitamente el árbol
de procesos. Tras la corrección no se mantiene ninguna inestabilidad conocida.

## 13. Cierre del plan

### Resultado frente a los criterios de salida

| Criterio | Evidencia final | Estado |
|---|---|---|
| Tres niveles sin fallos | Suite local: `26 passed`; CI verde | Cumple |
| Ruff y Pyrefly con código cero | Etapas visibles en Actions | Cumple |
| Casos trazables | `DISENO-DE-CASOS.md` y tabla de este plan | Cumple |
| Casos descartados justificados | Cuatro descartes documentados | Cumple |
| Sin secretos ni datos personales | Datos sintéticos y campos extra prohibidos | Cumple |
| Servidores cerrados y estado aislado | Fixtures verifican cierre y estado por prueba | Cumple |
| Inestabilidad tratada | Sin `skip`/`xfail`; sincronización E2E documentada | Cumple |

### Evidencia del pipeline

- [Ejecución roja controlada 36364212305](https://github.com/JulioRincones/ContaSur/actions/runs/36364212305): integración detectó que la API aceptaba un campo no declarado.
- [Ejecución verde 36364345551](https://github.com/JulioRincones/ContaSur/actions/runs/36364345551): la corrección prohibió campos extra y todas las etapas aprobaron.

### Riesgos aceptados y trabajo fuera de alcance

Se mantienen fuera autenticación, persistencia, carga concurrente, normativa
tributaria, accesibilidad exhaustiva y múltiples navegadores. El riesgo concreto
aceptado es que las celdas de `st.dataframe` no aparecieron en el árbol de
accesibilidad observado; los formularios y el resumen sí cumplen el criterio
de nombres accesibles. No se afirma cobertura sobre las exclusiones.
