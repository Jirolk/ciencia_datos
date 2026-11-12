"""Cuatro assets de Dagster para ejecutar el flujo de extremo a extremo."""

from dagster import (
    AssetExecutionContext,
    AssetSelection,
    Definitions,
    asset,
    define_asset_job,
    in_process_executor,
)

from generar_datos import generar_datos
from pipeline import ejecutar_ingesta
from reporte_calidad import reporte_calidad
from transformar import ejecutar_dbt


@asset(group_name="minimercado", description="Prepara los cinco archivos del minimercado.")
def generar_datos_asset(context: AssetExecutionContext) -> None:
    context.add_output_metadata(generar_datos())


@asset(
    group_name="minimercado",
    deps=[generar_datos_asset],
    description="Carga productos, vendedores, compras, ventas y stock en DuckDB.",
)
def ingesta_dlt_asset(context: AssetExecutionContext) -> None:
    carga = ejecutar_ingesta()
    context.add_output_metadata({"paquetes_cargados": len(carga.loads_ids)})


@asset(
    group_name="minimercado",
    deps=[ingesta_dlt_asset],
    description="Arma las tablas de análisis y ejecuta las pruebas de dbt.",
)
def dbt_transformations_asset(context: AssetExecutionContext) -> None:
    context.add_output_metadata(ejecutar_dbt())


@asset(
    group_name="minimercado",
    deps=[dbt_transformations_asset],
    description="Comprueba los totales y guarda los resultados del negocio.",
)
def reporte_calidad_asset(context: AssetExecutionContext) -> None:
    resultado = reporte_calidad()
    estadistica = resultado["01_estadistica"][0]
    context.add_output_metadata(
        {
            "controles": resultado["controles"],
            "dias": estadistica["dias"],
            "unidades_vendidas": estadistica["unidades_vendidas"],
            "facturacion_total": str(estadistica["facturacion_total"]),
        }
    )


assets = [generar_datos_asset, ingesta_dlt_asset, dbt_transformations_asset, reporte_calidad_asset]
minimercado_job = define_asset_job(
    "minimercado_job",
    selection=AssetSelection.all(),
    executor_def=in_process_executor,
    description="Prepara los datos, los carga, calcula los indicadores y revisa los resultados.",
)
defs = Definitions(assets=assets, jobs=[minimercado_job])
