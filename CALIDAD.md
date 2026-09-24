# CALIDAD.md

# Línea base de calidad - Sistema de Contabilidad para Empresas

## 1. Ficha de calidad ISO/IEC 25010

Para este proyecto se priorizan tres características de calidad relacionadas con el comportamiento que se busca verificar.

### 1.1 Adecuación funcional

**Justificación:**  
En un sistema contable es fundamental que las reglas implementadas produzcan los resultados definidos. Un error en el saldo, en el equilibrio de un asiento o en la clasificación de una operación afecta directamente la utilidad del sistema.

**Criterio verificable:**  
Todas las reglas de negocio declaradas en `README.md` deben tener al menos una prueba automatizada que compruebe su resultado esperado y que falle si se altera el comportamiento de la regla.

**Evidencia esperada:**  
Suite de pruebas ejecutada mediante `uv run pytest`.

---

### 1.2 Fiabilidad

**Justificación:**  
Los mismos datos contables deben producir resultados consistentes. El sistema no debe aceptar silenciosamente entradas inválidas ni producir resultados diferentes ante las mismas condiciones.

**Criterio verificable:**  
Las operaciones probadas con entradas válidas deben producir de forma consistente el resultado esperado, y las entradas que incumplen las precondiciones definidas deben ser rechazadas de manera controlada.

**Evidencia esperada:**  
Pruebas automatizadas para montos inválidos, cálculo de saldo, asientos y cuentas por pagar.

---

### 1.3 Mantenibilidad

**Justificación:**  
Las reglas contables pueden cambiar. Mantenerlas separadas, tipadas y acompañadas de pruebas permite detectar con rapidez cuándo una modificación cambia el comportamiento observable.

**Criterio verificable:**  
El proyecto debe finalizar sin errores en `ruff` y `pyrefly`, y cada regla de negocio declarada debe estar identificada y cubierta por una prueba que permita localizar qué comportamiento se rompió.

**Evidencia esperada:**

```bash
uv run ruff check .
uv run pyrefly check
uv run pytest
```

---

## 2. Tabla de trazabilidad

La tabla relaciona las necesidades del sistema con criterios verificables y con evidencia existente. Las evidencias que todavía no se hayan generado deben mantenerse explícitamente como `VACÍA` hasta que existan en el repositorio.

| Necesidad | Criterio | Evidencia de verificación | Evidencia de validación |
|---|---|---|---|
| Evitar movimientos con montos inválidos | Todo monto registrado debe ser > 0 | Prueba pytest RN-01 | VACÍA |
| Obtener correctamente el saldo de la empresa | Saldo = ingresos - egresos | Prueba pytest RN-02 | VACÍA |
| Evitar asientos contables descuadrados | Debe = Haber; un descuadre se rechaza al intentar registrarlo | Pruebas pytest RN-03 de clasificación y rechazo | Hallazgo 3: brecha confirmada y corregida mediante `registrar_asiento` |
| Identificar obligaciones vencidas | Una cuenta impaga con vencimiento anterior a la fecha evaluada se marca como vencida | Prueba pytest RN-04 | VACÍA |
| Informar la situación del saldo | > 0 SUPERAVIT; = 0 EQUILIBRIO; < 0 DEFICIT | Prueba pytest RN-05 | VACÍA |
| Mantener código analizable y tipado | Ruff y Pyrefly deben finalizar sin errores | Salida de ruff y pyrefly | No aplica directamente |

> Importante: sustituir `VACÍA` únicamente cuando exista evidencia real. No se debe inventar evidencia para completar la tabla.

---

## 3. Justificación de diagnósticos silenciados

### Estado inicial

No se han silenciado intencionalmente diagnósticos de `ruff` ni `pyrefly`.

Por lo tanto, actualmente no existen usos deliberados de:

- `# noqa`
- `# type: ignore`
- reglas de Ruff desactivadas para ocultar errores
- exclusiones destinadas únicamente a conseguir una ejecución en verde

Si posteriormente fuera necesario silenciar un diagnóstico, se documentará individualmente usando el siguiente formato.

### Plantilla

**Herramienta:**  
Ruff / Pyrefly

**Archivo y línea:**  
`ruta/archivo.py:línea`

**Diagnóstico original:**  
Descripción exacta del diagnóstico.

**Decisión:**  
Se mantiene el código y se silencia el diagnóstico.

**Justificación:**  
Explicación concreta de por qué el diagnóstico no corresponde en ese caso.

---

## 4. Hallazgos de la auditoría

Los siguientes apartados sirven como línea base. Los hallazgos definitivos deben corresponder a problemas realmente observados al ejecutar o revisar el programa.

### Hallazgo 1 - Defecto real reproducido mediante una prueba

**Estado:** CONFIRMADO Y CORREGIDO.

**Caso observado:** la interfaz Streamlit no podía importar el paquete del
proyecto.

Al ejecutar `uv run streamlit run app.py`, la aplicación terminaba con
`ModuleNotFoundError: No module named 'contabilidad'`. Pytest no revelaba el
problema porque su configuración añadía `src` al camino de importación, mientras
que Streamlit ejecutaba `app.py` sin esa ayuda. El proyecto tenía un layout
`src`, pero no declaraba cómo construir e instalar el paquete.

**Evidencia:**

1. Error observado al iniciar la interfaz: `ModuleNotFoundError` en
   `from contabilidad import ...`.
2. Causa: faltaban `[build-system]` y la selección del paquete
   `src/contabilidad` en `pyproject.toml`.
3. Corrección aplicada: configuración de Hatchling y ejecución de `uv sync`
   para instalar el proyecto.
4. Prueba de regresión:
   `test_regresion_paquete_disponible_fuera_del_directorio_del_proyecto`, que
   importa `contabilidad` desde un proceso ubicado en una carpeta temporal y
   sin depender del `PYTHONPATH` de Pytest.
5. Resultado posterior: `uv run pytest` finaliza con 9 pruebas aprobadas.

---

### Hallazgo 2 - Riesgo en valores límite

**Estado:** AUDITADO CON PRUEBAS.

Las reglas RN-01 y RN-05 poseen límites especialmente sensibles: monto `0` y saldo `0`. Una alteración de `>` a `>=`, o viceversa, puede modificar el comportamiento observable.

**Acción de auditoría:**  
Crear casos específicos para los valores inmediatamente relevantes al límite y comprobar que un cambio del operador provoque el fallo de la prueba correspondiente.

**Resultado:**  
La suite incluye los límites `0`, `1` y `-1` para RN-01, y los saldos `1`, `0`
y `-1` para RN-05. Las pruebas asociadas son
`test_rn_01_rechaza_montos_iguales_o_inferiores_a_cero`,
`test_rn_01_registra_movimientos_con_monto_mayor_que_cero` y
`test_rn_05_clasifica_superavit_equilibrio_y_deficit`.

---

### Hallazgo 3 - Hallazgo de validación

**Estado:** CONFIRMADO Y CORREGIDO.

**Situación:**  
La tabla de trazabilidad declara la necesidad de "evitar asientos contables
descuadrados". Sin embargo, RN-03 y sus pruebas solo verifican si Debe y Haber
son iguales. Al ingresar Debe `100` y Haber `90`, la interfaz muestra el mensaje
"Asiento descuadrado", pero no existe una operación de registro que pueda
rechazarse ni una garantía que impida continuar con ese asiento.

La suite completa puede terminar en verde porque comprueba correctamente la
clasificación `esta_cuadrado`. Aun así, el producto no satisface la necesidad más
amplia que quedó declarada: evitar que un asiento descuadrado sea aceptado por el
flujo contable.

**Por qué es un problema de validación:**
El código implementa correctamente la regla especificada y las pruebas detectan
si la comparación Debe/Haber se altera. No se encontró un error en esa
implementación. El problema es que el criterio verificable se redujo a
"detectar" un descuadre, mientras la necesidad pide "evitarlo". Por eso existe
una diferencia entre construir correctamente la función especificada y construir
el comportamiento que la necesidad declara.

**Evidencia observada:**

1. Necesidad declarada en la tabla: evitar asientos descuadrados.
2. `app.py`: el flujo recibe Debe y Haber y solo presenta un mensaje de estado.
3. En el estado auditado, RN-03 solo probaba la clasificación, no el rechazo de
   una operación.
4. Ejemplo reproducible: Debe `100`, Haber `90`; las pruebas siguen en verde y
   la interfaz se limita a informar la diferencia.

**Decisión:**
Se mantiene la necesidad de evitar asientos descuadrados. La corrección incorpora
`registrar_asiento`, que rechaza la operación con `ValueError` cuando Debe y
Haber no coinciden. La interfaz ejecuta esta operación mediante el botón
"Registrar asiento" y solo confirma el registro cuando el asiento está
cuadrado. La prueba `test_rn_03_rechaza_registro_de_asiento_descuadrado`
comprueba tanto el rechazo como la aceptación de un asiento válido.

---

## 5. Registro del defecto reproducido

Este apartado debe completarse cuando exista un defecto real.

**Defecto encontrado:**  
La aplicación Streamlit fallaba al iniciar con
`ModuleNotFoundError: No module named 'contabilidad'`.

**Regla afectada:**  
Requisito de ejecutabilidad y reproducibilidad del proyecto.

**Comportamiento esperado:**  
`app.py` debe poder importar el paquete `contabilidad` después de ejecutar
`uv sync`, con independencia del directorio desde el que Python resuelva el
módulo.

**Comportamiento observado:**  
La suite funcionaba gracias al `pythonpath` configurado para Pytest, pero
Streamlit no encontraba `contabilidad` y la interfaz no se ejecutaba.

**Prueba que reproduce el defecto:**  
`test_regresion_paquete_disponible_fuera_del_directorio_del_proyecto`.

**Corrección realizada:**  
Se agregó Hatchling como sistema de construcción, se declaró
`src/contabilidad` como paquete de la distribución y se sincronizó el entorno
con `uv sync`.

**Resultado después de corregir:**  
`uv run pytest` finaliza con 9 pruebas aprobadas.

---

## 6. Registro de cambios relevantes para la calidad

| Fecha | Cambio | Motivo | Evidencia |
|---|---|---|---|
| 2026-09-08 | Creación de línea base | Inicio del proyecto | README.md / CALIDAD.md |
| 2026-09-08 | Incorporación de pruebas | Verificar reglas de negocio | `uv run pytest`: 9 passed |
| 2026-09-08 | Revisión estática | Detectar problemas de código y tipos | `uv run ruff check .`: All checks passed; `uv run pyrefly check`: 0 errors |
| 2026-09-08 | Corrección de defecto real | Permitir que Streamlit importe el paquete instalado | `test_regresion_paquete_disponible_fuera_del_directorio_del_proyecto` |
| 2026-09-21 | Hallazgo de validación confirmado | Contrastar la necesidad de evitar asientos descuadrados con el comportamiento entregado | Hallazgo 3 y revisión de `app.py` / RN-03 |
| 2026-09-21 | Ampliación del análisis de tipos | Incluir la interfaz Streamlit en el alcance de Pyrefly | `project-includes = ["app.py", "src", "tests"]`; Pyrefly: 0 errores |
| 2026-09-21 | Corrección del hallazgo de validación | Rechazar el registro de asientos descuadrados | `registrar_asiento` y prueba de rechazo RN-03 |

## 7. Ensayo de mutaciones para la verificación en vivo

Se alteró temporalmente una condición de cada regla declarada y se ejecutó
`tests/unit/test_negocio.py` contra cada copia mutada. Las copias se crearon fuera del
repositorio y se eliminaron después del ensayo; el código productivo no fue
modificado por este procedimiento.

| Regla | Cambio temporal | Prueba que detectó el cambio | Resultado |
|---|---|---|---|
| RN-01 | `monto <= 0` por `monto < 0` | `test_rn_01_rechaza_montos_iguales_o_inferiores_a_cero` | 1 fallo |
| RN-02 | Restar egresos por sumarlos | `test_rn_02_calcula_saldo_como_ingresos_menos_egresos` | 1 fallo |
| RN-03 | `Debe == Haber` por `Debe != Haber` | Pruebas RN-03 de clasificación y rechazo | 2 fallos |
| RN-04 | Fecha de vencimiento `<` por `<=` | `test_rn_04_detecta_cuentas_vencidas_segun_fecha_y_pago` | 1 fallo |
| RN-05 | Saldo `> 0` por `>= 0` | Caso `EQUILIBRIO` de `test_rn_05_clasifica_superavit_equilibrio_y_deficit` | 1 fallo |

Los cinco cambios alteran comportamiento observable y fueron detectados. Para
explicar el resultado en vivo: cada prueba usa un valor que distingue ambos
operadores, por ejemplo `0` en RN-01/RN-05 y una fecha igual a la fecha de
evaluación en RN-04.

## 8. Conclusión de la línea base

La calidad de este proyecto no se evaluará por la cantidad de funcionalidades contables implementadas, sino por la capacidad de demostrar su comportamiento mediante evidencia. La línea base verificable queda cubierta porque `ruff`, `pyrefly` y `pytest` finalizan correctamente, existe evidencia para cada regla declarada y se reprodujo/corrigió un defecto real. La auditoría confirmó además una brecha de validación entre detectar y evitar asientos descuadrados. Se decidió mantener la necesidad de prevención y se corrigió el flujo para rechazar el registro cuando Debe y Haber no coinciden.

## 9. Evolución para la Evaluación Parcial 2

### 9.1 Observaciones de la EP1

El feedback docente otorgó 96/100. Los controles, la trazabilidad, el hallazgo
de validación y la reproducibilidad fueron evaluados como excelentes. La mejora
solicitada fue conservar un arbitraje concreto frente al agente y extender la
evidencia a integración y E2E.

Acciones aplicadas:

- El episodio concreto de propuesta, objeción y decisión se conserva en
  `README.md` y `DISENO-DE-CASOS.md`.
- Los casos aceptados y descartados tienen fundamento explícito.
- FastAPI agrega contratos observables de integración.
- Playwright comprueba desde el navegador el registro de un movimiento y el
  rechazo de un asiento descuadrado.
- La prueba E2E detectó que el resumen visual no se actualizaba tras registrar;
  se corrigió el flujo con un rerun y un mensaje conservado en sesión.

### 9.2 Pirámide de pruebas

| Nivel | Responsabilidad | Riesgo exclusivo |
|---|---|---|
| Unitario | Particiones, límites y decisiones del dominio | Operador o fórmula incorrecta |
| Integración | Contrato HTTP, serialización y conexión FastAPI-dominio | Campo, código o cuerpo incompatible |
| E2E | Recorrido visible en Streamlit con Chromium | Control ausente, rerun o estado de sesión defectuoso |

Los niveles no duplican el mismo objetivo. La cobertura detallada se encuentra
en `DISENO-DE-CASOS.md` y la estrategia en `PLAN-DE-PRUEBAS.md`.

### 9.3 Datos y privacidad

La suite usa únicamente montos, tipos y fechas sintéticas. No existen nombres,
RUT, correos, cuentas bancarias ni documentos reales. Integración crea un estado
en memoria por prueba y E2E elimina su estado al cerrar el servidor Streamlit.

### 9.4 Evidencia esperada de EP2

```bash
uv run pytest tests/unit
uv run pytest tests/integration
uv run pytest tests/e2e
uv run pytest
uv run ruff check .
uv run pyrefly check
```

Evidencia ejecutada el 24 de septiembre de 2026:

- Unitarias e integración: `21 passed`.
- E2E con Chromium: `1 passed`.
- Suite completa: `22 passed`.
- Ruff: `All checks passed!`.
- Pyrefly: `0 errors`.

Los tres niveles conviven en un único comando y cumplen los criterios de salida.
