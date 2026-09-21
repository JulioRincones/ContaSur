# Sistema de Contabilidad para Empresas

Proyecto desarrollado para la asignatura **PRO402 - Taller de Testing y Calidad de Software**.

## 1. Descripción del proyecto

Este proyecto corresponde a un sistema simplificado de contabilidad empresarial desarrollado en Python. Su objetivo es aplicar reglas de negocio contables que puedan ser verificadas mediante pruebas automatizadas.

Para esta primera evaluación se prioriza la calidad de la verificación por sobre la cantidad de funcionalidades. Por ello, el sistema se concentra en reglas de negocio pequeñas, observables y comprobables.

## 2. Alcance

El sistema permite trabajar con operaciones contables básicas de una empresa:

- Registrar movimientos de ingreso y egreso.
- Validar que los montos contables sean válidos.
- Calcular el saldo de la empresa.
- Determinar el estado de un documento según su fecha de vencimiento.
- Validar el equilibrio de un asiento contable.

No se requiere interfaz gráfica, base de datos ni API para esta etapa.

## 3. Reglas de negocio declaradas

### RN-01: Validación de montos
Un movimiento contable solo puede registrarse cuando su monto es mayor que cero. Los montos iguales o inferiores a cero deben ser rechazados.

### RN-02: Cálculo del saldo
El saldo contable se calcula como la suma de los ingresos menos la suma de los egresos.

`saldo = total_ingresos - total_egresos`

### RN-03: Equilibrio de un asiento contable
Un asiento se considera cuadrado únicamente cuando el total del Debe es exactamente igual al total del Haber.

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
|-- src/
|   `-- contabilidad/
|       |-- __init__.py
|       `-- negocio.py
`-- tests/
    `-- test_negocio.py
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

## 8. Ejecución de los controles de calidad

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

### Pytest

```bash
uv run pytest
```

Resultado esperado: todas las pruebas terminan en verde.

## 9. Pruebas y reglas de negocio

La suite debe incluir, como mínimo, una prueba capaz de fallar por cada regla declarada:

| Regla | Comportamiento verificado |
|---|---|
| RN-01 | Rechazo de montos iguales o inferiores a cero |
| RN-02 | Cálculo correcto de ingresos menos egresos |
| RN-03 | Detección de asientos cuadrados y descuadrados |
| RN-04 | Detección de cuentas vencidas según fecha y estado de pago |
| RN-05 | Clasificación correcta de superávit, equilibrio y déficit |

Además, se debe conservar una prueba que reproduzca un defecto real encontrado durante el desarrollo y documentar su corrección en `CALIDAD.md`.

## 10. Uso de IA o agentes

Durante el desarrollo se utilizó **ChatGPT** como agente de apoyo.

### Para qué se utilizó

- Proponer una estructura inicial del proyecto.
- Proponer reglas de negocio apropiadas para un sistema contable simplificado.
- Ayudar a redactar casos de prueba.
- Revisar la estructura de `README.md` y `CALIDAD.md`.
- Proponer criterios verificables relacionados con ISO/IEC 25010.

### Qué revisé o corregí personalmente

Las propuestas del agente fueron revisadas antes de incorporarlas al proyecto. Se verificó que las reglas fueran coherentes con el código implementado y que las pruebas comprobaran comportamiento observable en vez de limitarse a ejecutar líneas de código.

### Error o límite detectado

Una limitación del agente es que puede proponer reglas, pruebas o documentación que parecen correctas sin conocer el comportamiento real del programa. Por esta razón, cada prueba propuesta debe ser ejecutada y revisada para comprobar que realmente falla cuando se altera la regla correspondiente.

### Revisión adversarial

En una revisión adversarial, el primer análisis propuso aceptar una prueba por el solo hecho de terminar en verde. Una segunda revisión objetó que una prueba en verde no demuestra por sí sola que detecte cambios en la regla de negocio. Se decidió conservar únicamente pruebas con aserciones significativas y comprobar que fallen al modificar intencionalmente la regla evaluada.

## 11. Autor

Nombre: Julio Rincones

Asignatura: PRO402 - Taller de Testing y Calidad de Software

Docente: Diego Obando
