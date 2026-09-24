# Sistema de Contabilidad para Empresas

Proyecto desarrollado para la asignatura **PRO402 - Taller de Testing y Calidad de Software**.

## 1. Descripción del proyecto

Este proyecto corresponde a un sistema simplificado de contabilidad empresarial desarrollado en Python. Su objetivo es aplicar reglas de negocio contables que puedan ser verificadas mediante pruebas automatizadas.

El proyecto evoluciona de forma incremental. La segunda evaluación mantiene las
reglas originales y agrega diseño formal de casos, una API consumible y una
suite automatizada en niveles unitario, integración y extremo a extremo.

## 2. Alcance

El sistema permite trabajar con operaciones contables básicas de una empresa:

- Registrar movimientos de ingreso y egreso.
- Validar que los montos contables sean válidos.
- Calcular el saldo de la empresa.
- Determinar el estado de un documento según su fecha de vencimiento.
- Validar y rechazar asientos contables descuadrados.
- Consumir las reglas mediante una API FastAPI.
- Recorrer los flujos principales desde una interfaz Streamlit.

No incluye base de datos, autenticación, facturación electrónica ni datos
personales. El estado de la interfaz y de la API se mantiene en memoria.

## 3. Reglas de negocio declaradas

### RN-01: Validación de montos
Un movimiento contable solo puede registrarse cuando su monto es mayor que cero. Los montos iguales o inferiores a cero deben ser rechazados.

### RN-02: Cálculo del saldo
El saldo contable se calcula como la suma de los ingresos menos la suma de los egresos.

`saldo = total_ingresos - total_egresos`

### RN-03: Equilibrio de un asiento contable
Un asiento se considera cuadrado únicamente cuando el total del Debe es exactamente igual al total del Haber. Los asientos descuadrados deben ser rechazados al intentar registrarlos.

### RN-04: Estado de una cuenta por pagar
Una cuenta se considera vencida cuando no está pagada y su fecha de vencimiento es anterior a la fecha de evaluación. Si fue pagada, no se considera vencida.

### RN-05: Clasificación del saldo
El sistema clasifica el resultado de la empresa de la siguiente forma:

- Saldo mayor que 0: `SUPERAVIT`
- Saldo igual a 0: `EQUILIBRIO`
- Saldo menor que 0: `DEFICIT`

Estas reglas constituyen el comportamiento observable que debe estar cubierto por la suite de pruebas.

## 4. Tecnologías y herramientas

- Python
- uv: gestión del proyecto, dependencias y entorno.
- Streamlit: interfaz gráfica web local.
- FastAPI: interfaz HTTP consumible y contratos de integración.
- Playwright: pruebas de extremo a extremo con Chromium.
- ruff: análisis estático.
- pyrefly: verificación de tipos.
- pytest: pruebas automatizadas.

## 5. Estructura sugerida

```text
contabilidad-empresas/
|-- .python-version
|-- .gitignore
|-- pyproject.toml
|-- uv.lock
|-- README.md
|-- CALIDAD.md
|-- DISENO-DE-CASOS.md
|-- PLAN-DE-PRUEBAS.md
|-- app.py
|-- src/
|   `-- contabilidad/
|       |-- __init__.py
|       |-- api.py
|       `-- negocio.py
`-- tests/
    |-- unit/
    |-- integration/
    `-- e2e/
```

## 6. Instalación

### Requisito previo

Tener `uv` instalado.

### Clonar el repositorio

```bash
git clone https://github.com/JulioRincones/ContaSur.git
cd ContaSur
```

### Instalar las dependencias

```bash
uv sync
uv run playwright install chromium
```

La versión de Python utilizada por el proyecto debe quedar fijada en `.python-version`.

## 7. Ejecución de la interfaz gráfica

La interfaz permite registrar movimientos, revisar el saldo, clasificar el
resultado, validar asientos contables y evaluar cuentas por pagar desde un panel
web local.

```bash
uv run streamlit run app.py
```

Streamlit abrirá la aplicación en el navegador. Si no se abre automáticamente,
usa la URL local que aparece en la terminal.

## 8. Ejecución de la API

```bash
uv run uvicorn contabilidad.api:app --reload
```

La documentación interactiva queda disponible en
`http://127.0.0.1:8000/docs` y el control de salud en
`http://127.0.0.1:8000/api/salud`.

## 9. Ejecución de la suite por nivel

### Pruebas unitarias

```bash
uv run pytest tests/unit
```

Comprueban particiones, límites y decisiones de las reglas sin interfaz.

### Pruebas de integración

```bash
uv run pytest tests/integration
```

Comprueban contratos HTTP, serialización, estados de respuesta, aislamiento y
conexión entre FastAPI y el dominio.

### Pruebas extremo a extremo

```bash
uv run pytest tests/e2e
```

Playwright levanta Streamlit en un puerto libre, ejecuta el recorrido con
Chromium y cierra el servidor al terminar.

### Suite completa

```bash
uv run pytest
```

## 10. Ejecución de los controles de calidad

### Ruff

```bash
uv run ruff check .
```

Resultado esperado: el análisis termina sin errores.

### Pyrefly

```bash
uv run pyrefly check
```

Resultado esperado: la verificación de tipos termina sin errores.

## 11. Diseño y plan de pruebas

- `DISENO-DE-CASOS.md`: particiones de equivalencia, valores límite, tablas de
  decisión, casos descartados y vínculo con pruebas.
- `PLAN-DE-PRUEBAS.md`: alcance, riesgos, estrategia, trazabilidad, datos y
  criterios de entrada/salida según ISO/IEC/IEEE 29119.

## 12. Pruebas y reglas de negocio

La suite debe incluir, como mínimo, una prueba capaz de fallar por cada regla declarada:

| Regla | Comportamiento verificado | Mutación ensayada |
|---|---|---|
| RN-01 | Rechazo de montos iguales o inferiores a cero | Cambiar `<= 0` por `< 0` |
| RN-02 | Cálculo correcto de ingresos menos egresos | Sumar egresos en vez de restarlos |
| RN-03 | Detección y rechazo de asientos descuadrados | Cambiar `Debe == Haber` por `Debe != Haber` |
| RN-04 | Detección de cuentas vencidas según fecha y estado de pago | Cambiar fecha `<` por `<=` |
| RN-05 | Clasificación correcta de superávit, equilibrio y déficit | Cambiar saldo `> 0` por `>= 0` |

Además, se debe conservar una prueba que reproduzca un defecto real encontrado durante el desarrollo y documentar su corrección en `CALIDAD.md`.

## 13. Uso de IA o agentes

Durante el desarrollo se utilizó **ChatGPT** como agente de apoyo.

### Para qué se utilizó

- Proponer una estructura inicial del proyecto.
- Proponer reglas de negocio apropiadas para un sistema contable simplificado.
- Ayudar a redactar casos de prueba.
- Revisar la estructura de `README.md` y `CALIDAD.md`.
- Proponer criterios verificables relacionados con ISO/IEC 25010.
- Proponer particiones, límites, tablas de decisión y niveles para la EP2.
- Implementar una primera versión de FastAPI, fixtures y Playwright.

### Qué revisé o corregí personalmente

Las propuestas del agente fueron revisadas antes de incorporarlas al proyecto. Se verificó que las reglas fueran coherentes con el código implementado y que las pruebas comprobaran comportamiento observable en vez de limitarse a ejecutar líneas de código.

### Error o límite detectado

Una limitación del agente es que puede proponer reglas, pruebas o documentación que parecen correctas sin conocer el comportamiento real del programa. Por esta razón, cada prueba propuesta debe ser ejecutada y revisada para comprobar que realmente falla cuando se altera la regla correspondiente.

### Episodio concreto de auditoría del agente

**Propuesta:** el agente sugirió ampliar RN-04 considerando vencida una cuenta
impaga cuya fecha de vencimiento fuera igual a la fecha de evaluación. También
propuso repetir todas las reglas en Playwright y usar datos de un proveedor
"realista".

**Objeción:** el caso de igualdad contradice la regla declarada, que exige una
fecha anterior. Repetir todas las combinaciones en E2E no agrega un riesgo nuevo
y vuelve la suite lenta. Los datos identificables tampoco son necesarios.

**Decisión de Julio:** se rechazaron esas tres propuestas. Se conservaron las
particiones anterior/igual/posterior de RN-04 respetando el resultado actual, un
solo flujo E2E vertical y datos completamente sintéticos. El detalle de casos
aceptados y descartados está en `DISENO-DE-CASOS.md`.

**Antes y después:** antes, RN-02 no cubría colección vacía ni colecciones de un
solo tipo; RN-03 no ejercitaba ambos lados del descuadre; RN-04 no incluía fecha
posterior. Después se agregaron esos casos unitarios y se vinculó cada uno con
su partición formal. La evidencia queda en `tests/unit/test_negocio.py` y en el
commit de la EP2 que incorpora estos cambios.

## 14. Autor

Nombre: Julio Rincones

Asignatura: PRO402 - Taller de Testing y Calidad de Software

Docente: Diego Obando
