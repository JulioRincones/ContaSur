# Pruebas no funcionales

## 1. Método

Los criterios de este documento se fijaron antes de ejecutar las mediciones de
la evaluación final. Los datos son sintéticos y no contienen información
personal. La evidencia automatizada usa el marcador `nonfunctional`:

```bash
uv run pytest -m nonfunctional
```

## 2. Rendimiento

### Operación crítica

Cálculo del saldo, porque recorre todos los movimientos y alimenta el resumen
principal.

### Criterio previo

Calcular el saldo de 10.000 movimientos en memoria debe tardar menos de `0,5 s`
en el entorno local y en GitHub Actions. El umbral deja margen a máquinas
compartidas y detecta una degradación de varios órdenes de magnitud; no pretende
ser una capacidad productiva de carga.

### Datos y prueba

- 5.000 ingresos y 5.000 egresos de `$100`.
- Saldo esperado: `$0`.
- Prueba: `test_rendimiento_calcula_diez_mil_movimientos_en_medio_segundo`.

### Resultado

Pendiente de medición inicial.

## 3. Seguridad de entrada

### Riesgo

Que la API confíe en campos enviados por el cliente, acepte tipos fuera del
contrato o exponga trazas internas al rechazar solicitudes.

### Criterio previo

- Un tipo de movimiento no declarado debe responder HTTP `422`.
- Un campo adicional no declarado debe responder HTTP `422`.
- Ninguna respuesta de rechazo debe contener la palabra `traceback`.

### Datos y prueba

Se envían el tipo sintético `transferencia` y un campo inesperado llamado `rut`.
El valor del campo también es ficticio y existe solo para comprobar que el
servidor no lo acepta ni lo almacena.

Prueba: `test_seguridad_rechaza_tipo_y_campos_no_declarados`.

### Resultado

Pendiente de ejecución inicial.

## 4. Usabilidad y accesibilidad

### Persona y recorrido

Persona administrativa que usa teclado o tecnología de asistencia para
registrar un movimiento, registrar un asiento y marcar una cuenta como pagada.

### Criterio previo

El encabezado principal y los controles críticos deben estar expuestos con rol
y nombre accesible en Chromium:

- Campo `Monto` y botón `Registrar movimiento`.
- Campos `Debe` y `Haber`, y botón `Registrar asiento`.
- Casilla `Pagada`.

### Evidencia automatizada

Prueba: `test_accesibilidad_controles_criticos_tienen_nombre`, que localiza cada
control mediante roles y etiquetas accesibles de Playwright.

### Hallazgos exploratorios

1. Durante la EP2, después de registrar un movimiento, el mensaje de éxito era
   visible pero el resumen seguía mostrando `$0` hasta otra interacción. Para
   una persona administrativa esto comunicaba dos resultados incompatibles. Se
   corrigió conservando el mensaje en sesión y ejecutando `st.rerun()`; el flujo
   E2E protege la corrección.
2. El historial usa el componente interactivo `st.dataframe`. Sus controles
   tienen nombre, pero el contenido de las celdas no apareció en el árbol de
   accesibilidad observado por Playwright. El resumen y los formularios siguen
   siendo operables, pero una persona con lector de pantalla podría no acceder
   al detalle del historial. Se acepta temporalmente este riesgo por el alcance
   educativo y se propone reemplazarlo por una tabla HTML accesible en una
   siguiente iteración.

### Resultado

Pendiente de ejecución inicial.

## 5. Privacidad

No se contabiliza como una de las tres categorías exigidas porque ContaSur no
trata datos personales en su alcance actual. Se mantiene minimización: montos,
fechas y tipos contables sintéticos; no se almacenan nombres, RUT, correos,
teléfonos ni cuentas bancarias. Si el producto incorpora personas identificadas,
deberá definir finalidad, conservación y mecanismos para ejercer derechos antes
de aceptar esos datos.
