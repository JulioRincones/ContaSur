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
- Instalación del paquete y controles Ruff/Pyrefly.

### Excluido

- Persistencia en base de datos y concurrencia multiusuario.
- Autenticación, autorización y datos personales.
- Tributación, facturación electrónica y normativa contable externa.
- Rendimiento, carga, accesibilidad exhaustiva y múltiples navegadores.
- Despliegue productivo y recuperación ante desastres.

Estas exclusiones corresponden al alcance educativo actual y no se presentan
como comportamientos verificados.

## 3. Riesgos del producto

| Riesgo | Prioridad | Calidad ISO 25010 | Respuesta de prueba |
|---|---|---|---|
| R1: aceptar montos o asientos inválidos | Alta | Adecuación funcional, fiabilidad | Límites unitarios, error HTTP y rechazo E2E |
| R2: calcular o clasificar mal el saldo | Alta | Adecuación funcional | Particiones unitarias y resumen de integración |
| R3: contrato API incompatible con consumidores | Alta | Compatibilidad, fiabilidad | Estados HTTP y cuerpos exactos de integración |
| R4: interfaz no actualiza estado o pierde el rechazo | Alta | Adecuación funcional | Recorrido Playwright con navegador real |
| R5: pruebas con estado compartido o intermitentes | Media | Fiabilidad, mantenibilidad | Fixture aislado y servidor/puerto por sesión E2E |
| R6: exposición de datos personales | Baja en el alcance actual | Seguridad | Datos sintéticos y minimizados |
| R7: paquete no instalable fuera del repositorio | Media | Portabilidad, mantenibilidad | Regresión de empaquetado |

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

| Riesgo | Requisito | Casos | Pruebas automatizadas |
|---|---|---|---|
| R1 | RN-01 | CU-RN01-01..03, CI-RN01-01 | Pruebas RN-01 y `test_api_rechaza_movimiento_con_monto_cero` |
| R1 | RN-03 | CU-RN03-01..04, CI-RN03-01, CE-RN03-01 | Pruebas RN-03, rechazo API y flujo Playwright |
| R2 | RN-02/RN-05 | CU-RN02-01..04, CI-RN02-01, CU-RN05-01..03 | Pruebas de saldo, resumen y clasificación |
| R3 | Contrato HTTP | CI-RN01-01, CI-RN02-01, CI-RN03-01, CI-RN04-01..03 | `tests/integration/test_api.py` |
| R4 | Flujo web | CE-FLUJO-01 | `tests/e2e/test_streamlit.py` |
| R5 | Aislamiento | Todos los CI/CE | Fixtures `cliente` y `servidor_streamlit` |
| R6 | Protección de datos | Todos | Literales sintéticos documentados |
| R7 | Ejecutabilidad | Regresión EP1 | `test_regresion_paquete_disponible_fuera_del_directorio_del_proyecto` |

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
uv run pytest
uv run ruff check .
uv run pyrefly check
```

## 11. Responsabilidades y evidencia

Julio Rincones revisa las reglas, acepta o descarta los casos y entrega el
repositorio. El agente propone estructura, casos y automatización; sus propuestas
se auditan en `DISENO-DE-CASOS.md` y `README.md`. La salida de Pytest, Ruff,
Pyrefly y el historial Git constituyen la evidencia reproducible.
