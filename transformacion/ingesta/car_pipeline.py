import csv
from pathlib import Path

import dlt

ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = ROOT / "data" / "car_sales.csv"
DB_PATH = ROOT / "car_ingestion.duckdb"


@dlt.resource(name="raw_car_sales", write_disposition="replace")
def car_sales_resource():
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row["Car Year"] = int(row["Car Year"])
            row["Sale Price"] = float(row["Sale Price"])
            row["Commission Rate"] = float(row["Commission Rate"])
            row["Commission Earned"] = float(row["Commission Earned"])
            yield row


if __name__ == "__main__":
    pipeline = dlt.pipeline(
        pipeline_name="car_ingestion",
        destination=dlt.destinations.duckdb(str(DB_PATH)),
        dataset_name="bronze_raw",
    )
    load_info = pipeline.run(car_sales_resource())
    print("Carga exitosa a la capa bronce:", load_info)
