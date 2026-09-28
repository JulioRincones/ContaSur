# Defensa oral de ContaSur

Este documento resume mis respuestas y la evidencia que puedo abrir durante la
defensa. No reemplaza la explicación oral: sirve para ubicar rápidamente el
código, las pruebas y las decisiones.

## 1. ¿Qué prueba fue la más difícil de escribir y por qué?

La más difícil fue
`test_flujo_registra_ingreso_y_rechaza_asiento_descuadrado`, la prueba E2E de
Streamlit con Playwright.

No bastaba con llamar una función. La prueba debía:

- Encontrar un puerto libre.
- Levantar un servidor Streamlit real.
- Esperar su endpoint de salud.
- Abrir Chromium y usar los formularios como una persona.
- Esperar el rerun asíncrono de Streamlit.
- Cerrar el árbol de procesos incluso si la prueba fallaba.

Durante su construcción encontró un defecto real: después de registrar un
ingreso aparecía el mensaje de éxito, pero el resumen seguía mostrando `$0`
porque se había calculado antes de actualizar la sesión. Lo corregí guardando el
mensaje y ejecutando `st.rerun()`. Esta prueba fue difícil porque coordinaba
navegador, servidor, sesión y tiempos; una unitaria no podía detectar ese fallo
visual.

**Evidencia para abrir:** `tests/e2e/test_streamlit.py` y
`registrar_movimiento_ui` en `app.py`.

## 2. ¿Qué parte sigue sin cubrir y qué riesgo acepté?

La limitación más concreta es el historial implementado con `st.dataframe`.
Durante el recorrido exploratorio, los controles del componente aparecieron en
el árbol de accesibilidad, pero no el contenido de sus celdas. Una persona que
usa lector de pantalla podría operar los formularios y consultar el resumen,
pero podría no acceder al detalle completo del historial.

Acepté temporalmente ese riesgo porque el alcance es educativo, no maneja datos
persistentes y el flujo principal sí tiene nombres accesibles comprobados. No
afirmo que la aplicación tenga accesibilidad completa. La siguiente mejora sería
presentar el historial con una tabla HTML semántica y probar su lectura.

También permanecen fuera de alcance autenticación, persistencia, concurrencia,
normativa tributaria y navegadores distintos de Chromium. Están declarados, no
ocultos.

**Evidencia para abrir:** secciones de alcance y cierre en
`PLAN-DE-PRUEBAS.md`, y hallazgo de accesibilidad en `NO-FUNCIONALES.md`.

## 3. ¿De dónde salió cada umbral y cuándo lo escribí?

Los criterios quedaron escritos antes de medir, en el commit `0e45834`
(`test: definir criterios finales y activar CI`). En ese commit los resultados
todavía figuraban como pendientes.

### Rendimiento

- **10.000 movimientos:** volumen artificial suficientemente mayor que el uso
  manual de este prototipo para ejercitar el recorrido completo de la lista.
- **0,5 segundos:** presupuesto deliberadamente holgado para una operación en
  memoria y para un runner compartido de GitHub. Busca detectar una degradación
  grande, no prometer capacidad productiva.
- **Resultado posterior:** `0,002857 s`, aproximadamente `0,57 %` del umbral.

No elegí `0,5 s` después de ver `0,002857 s`; el historial Git demuestra el
orden.

### Seguridad

El criterio es binario, no temporal: `100 %` de las entradas de las dos clases
fuera de contrato deben responder `422`, y `0` respuestas pueden contener
`traceback`. Las clases son tipo de movimiento inválido y campo adicional.

### Accesibilidad

El número **7** corresponde a los siete elementos críticos del recorrido
declarado antes de ejecutar: encabezado, Monto, Registrar movimiento, Debe,
Haber, Registrar asiento y Pagada. El criterio exige `7 de 7` con nombre
accesible; no intenta medir toda la WCAG.

**Evidencia para abrir:** historial de `NO-FUNCIONALES.md`, commit `0e45834` y
prueba `tests/nonfunctional/test_rendimiento.py`.

## 4. Si cambia una regla, ¿qué prueba y etapa se ponen rojas?

Elijo RN-04: una cuenta está vencida cuando no está pagada y su fecha de
vencimiento es estrictamente anterior a la evaluación.

Si alguien cambia:

```python
return not cuenta.pagada and cuenta.fecha_vencimiento < fecha_evaluacion
```

por una condición que use `cuenta.pagada`, se pone roja
`test_rn_04_detecta_cuentas_vencidas_segun_fecha_y_pago` en la etapa
**Pruebas unitarias**. Las filas de integración de
`test_api_evalua_cuenta_segun_contrato` también fallan porque la API utiliza esa
misma regla.

Esto ya se comprobó en la EP2: la mutación produjo tres fallos. Si se cambiara
solo el contrato HTTP, por ejemplo `409` por `400`, fallaría integración, no la
unitaria. Si se renombrara el botón Registrar asiento, fallaría E2E.

**Evidencia para abrir:** `cuenta_esta_vencida`, las pruebas RN-04 y el PDF de
procedimiento de mutación.

## 5. ¿Qué dijo un agente que estaba equivocado y cómo lo detecté?

El agente propuso considerar vencida una cuenta impaga cuya fecha de
vencimiento fuera igual a la fecha de evaluación.

La propuesta parecía razonable desde lenguaje cotidiano, pero contradecía RN-04,
que declara una fecha **anterior**, no anterior o igual. Lo detecté contrastando
la propuesta con el README y la tabla de decisión. Por eso conservé tres
particiones distintas: día anterior, mismo día y día posterior; el mismo día no
está vencido.

También hubo una propuesta técnica insuficiente: usar un transporte ASGI
asíncrono para integración. Las pruebas de integración pasaban solas, pero la
suite completa chocaba con el bucle que Playwright administraba. Lo descubrí al
ejecutar `uv run pytest`, no al ejecutar niveles separados, y lo reemplacé por
Uvicorn con HTTP real.

**Evidencia para abrir:** auditoría del agente en `DISENO-DE-CASOS.md` y
`README.md`, y fixture `cliente` en `tests/integration/test_api.py`.

## 6. Tres líneas del pipeline

### Línea 30: `run: uv sync --locked`

Instala exactamente el entorno resuelto en `uv.lock`, incluida la versión de
Python fijada. Si la quitara, Ruff, Pyrefly, FastAPI, pytest y Playwright podrían
no estar disponibles, y el runner dejaría de reproducir el proyecto.

### Línea 33: `run: uv run playwright install --with-deps chromium`

Instala Chromium y las bibliotecas del sistema que necesita en Linux. El paquete
Python de Playwright no incluye por sí solo el navegador. Si la quitara, la etapa
E2E fallaría al intentar lanzar Chromium.

### Línea 48: `run: uv run pytest tests/e2e`

Ejecuta el recorrido real de Streamlit con navegador. Si la quitara, el pipeline
podría quedar verde aunque desapareciera un botón, el resumen no se actualizara
o el rechazo no fuera visible. Las unitarias y la API no observan esos defectos.

**Evidencia para abrir:** `.github/workflows/quality.yml` y la ejecución verde
de GitHub Actions.

## Resumen breve

1. La prueba más difícil fue E2E por la coordinación de servidor, navegador,
   rerun y limpieza; además encontró el saldo visual desactualizado.
2. Acepté la limitación accesible del historial, pero la declaré y mantuve
   operables los controles críticos.
3. Los criterios se fijaron en `0e45834` antes de medir.
4. Un cambio en RN-04 rompe la unitaria de RN-04 y también sus contratos de
   integración.
5. Rechacé "vence hoy = vencida" porque contradice la regla estricta.
6. Sin sincronización no hay entorno, sin Chromium no hay navegador y sin la
   etapa E2E los fallos visibles no bloquean el cambio.
