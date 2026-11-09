# Relación con los materiales de clase

Los ejemplos de las clases usan ventas de autos. En este proyecto se aplican al
minimercado; los archivos de clase son referencias, no nuevas reglas de entrega.

| Material | Qué se aplicó | Dónde se ve |
| --- | --- | --- |
| 02_arquitectura_contenedores_desarrollo.pdf, págs. 10–13 | Entorno reproducible, archivos persistentes y trabajo con ramas | README y uv.lock; validación en Codespaces pendiente |
| 03_Dominando dlt.pdf, págs. 6–13 | Recursos, destino DuckDB, tipos y estrategia de carga | pipeline.py; cinco recursos con replace y claves del origen |
| 04_DuckDB_y_dbt.pdf, págs. 19–39 | source(), ref(), staging, hechos, dimensiones y pruebas | dbt_project/models y sus archivos YAML |
| 04_01_modelado.pdf, págs. 5–9 | Grano y dimensiones compartidas | fct_ventas, fct_compras, dim_productos, dim_vendedores y dim_fecha |
| 05_Orquestación con Dagster.pdf, págs. 8–16 y 28 | Dependencias con deps, metadatos y rutas claras | orchestration/definitions.py y transformar.py |
| 06_Análisis numérico y OLAP con DuckDB.pdf, págs. 20–28 | Perfilado, conciliación y subtotales | reporte_calidad.py y consultas 06 y 07 de sql/ |

## Decisiones que conviene poder explicar

- **Grano:** una fila de venta es una línea de un producto. El identificador no
  agrupa varios productos dentro de un ticket.
- **Claves:** productos y vendedores conservan los IDs estables del origen.
  Las pruebas comprueban su unicidad y las relaciones.
- **Calendario:** tiene una fila por día del período. Esto permite incluir los
  días sin ventas al calcular los promedios.
- **Carga completa:** replace evita acumular la misma simulación al repetirla.
  Esta versión guarda la foto actual; un histórico de lotes sería una mejora.
- **Inventario:** es el stock inicial más entradas menos salidas. La rotación
  divide unidades vendidas por el promedio del stock al cierre de cada día.
- **Costo:** se usa el promedio ponderado del período completo. No es FIFO ni
  promedio móvil; compras tardías pueden cambiar la estimación retrospectiva.
- **Dagster:** deps declara el orden porque los datos se intercambian mediante
  archivos y DuckDB. Las cifras de cada etapa quedan como metadatos.
- **dbt:** build ejecuta modelos y pruebas. Un fallo detiene el paso y evita
  presentar el reporte final como correcto.
- **OLAP:** la consulta 07 incluye detalle mensual por categoría, subtotales por
  mes y un total general; las banderas distinguen cada nivel.

Los apuntes también presentan incrementales, snapshots, sensors, schedules y
simulaciones estadísticas. La consigna no exige incorporar todos esos ejemplos.
Se priorizó una ejecución manual completa que se pueda repetir y explicar.
