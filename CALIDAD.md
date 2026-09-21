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
| Evitar asientos contables descuadrados | Debe = Haber | Prueba pytest RN-03 | VACÍA |
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

**Caso observado:** tratamiento incorrecto de un asiento descuadrado.

Durante la auditoría se reprodujo una mutación defectuosa en
`AsientoContable.esta_cuadrado`, donde el resultado se calculaba con
`self.debe != self.haber`. Esta condición marcaba como cuadrado un asiento con
Debe `100` y Haber `90`.

**Evidencia:**

1. Código defectuoso reproducido: `return self.debe != self.haber`.
2. Prueba que falla: `test_regresion_rn_03_asiento_descuadrado_no_debe_aceptarse_como_cuadrado`.
3. Corrección aplicada: `return self.debe == self.haber`.
4. Resultado posterior: `uv run pytest` finaliza con 9 pruebas aprobadas.

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

**Estado:** CASO PROPUESTO; DEBE VALIDARSE CON EL DOMINIO ANTES DE PRESENTARLO COMO HALLAZGO REAL.

**Situación:**  
Supongamos que RN-04 define que una cuenta se considera vencida solamente cuando `fecha_vencimiento < fecha_actual`. La implementación y todas las pruebas podrían cumplir perfectamente esa definición.

Sin embargo, durante una revisión con la necesidad real del usuario se podría descubrir que una factura que vence **hoy** debe aparecer como vencida a partir de una condición determinada por el negocio. Si el requisito real fuera ese, el sistema podría aprobar toda su suite y aun así entregar una clasificación que no satisface la necesidad.

**Por qué sería un problema de validación:**  
La implementación puede coincidir exactamente con la regla documentada y las pruebas pueden verificarla correctamente. El problema estaría en que la regla especificada no representa la necesidad real del usuario. Por ello, no sería necesariamente un error de programación, sino una discrepancia entre lo construido y lo que el sistema debía hacer.

**Evidencia de validación requerida:**  
Confirmación de la regla correcta con el responsable o usuario del proceso contable y registro del caso observado.

---

## 5. Registro del defecto reproducido

Este apartado debe completarse cuando exista un defecto real.

**Defecto encontrado:**  
Una mutación defectuosa de RN-03 usaba `self.debe != self.haber` para
determinar si un asiento estaba cuadrado.

**Regla afectada:**  
RN-03: Equilibrio de un asiento contable.

**Comportamiento esperado:**  
Un asiento solo se considera cuadrado cuando el Debe es exactamente igual al
Haber.

**Comportamiento observado:**  
Un asiento con Debe `100` y Haber `90` era clasificado como cuadrado durante la
mutación defectuosa.

**Prueba que reproduce el defecto:**  
`test_regresion_rn_03_asiento_descuadrado_no_debe_aceptarse_como_cuadrado`.

**Corrección realizada:**  
Se reemplazó la comparación defectuosa por `self.debe == self.haber`.

**Resultado después de corregir:**  
`uv run pytest` finaliza con 9 pruebas aprobadas.

---

## 6. Registro de cambios relevantes para la calidad

| Fecha | Cambio | Motivo | Evidencia |
|---|---|---|---|
| 2026-09-08 | Creación de línea base | Inicio del proyecto | README.md / CALIDAD.md |
| 2026-09-08 | Incorporación de pruebas | Verificar reglas de negocio | `uv run pytest`: 9 passed |
| 2026-09-08 | Revisión estática | Detectar problemas de código y tipos | `uv run ruff check .`: All checks passed; `uv run pyrefly check`: 0 errors |
| 2026-09-08 | Corrección de defecto real | Convertir defecto encontrado en prueba de regresión | `test_regresion_rn_03_asiento_descuadrado_no_debe_aceptarse_como_cuadrado` |

## 7. Conclusión de la línea base

La calidad de este proyecto no se evaluará por la cantidad de funcionalidades contables implementadas, sino por la capacidad de demostrar su comportamiento mediante evidencia. La línea base verificable queda cubierta porque `ruff`, `pyrefly` y `pytest` finalizan correctamente, existe evidencia para cada regla declarada y se reprodujo/corrigió un defecto real. La validación con el dominio se mantiene pendiente hasta contar con confirmación externa real.
