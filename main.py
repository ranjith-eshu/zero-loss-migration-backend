
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io

app = FastAPI(title="Zero-Loss Migration API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "project": "Intelligent Zero-Loss Data Migration Platform",
        "status": "Backend running"
    }

@app.post("/validate")
async def validate_csv(file: UploadFile = File(...)):
    try:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))

        if "customer_id" not in df.columns:
            return {
                "status": "FAIL",
                "error": "CSV must contain customer_id column"
            }

        duplicate_count = int(
            df["customer_id"].duplicated().sum()
        )

        null_ids = int(df["customer_id"].isna().sum())

        return {
            "file_name": file.filename,
            "records": int(len(df)),
            "duplicate_ids": duplicate_count,
            "null_customer_ids": null_ids,
            "columns": list(df.columns),
            "status": "PASS" if (
                duplicate_count == 0 and null_ids == 0
            ) else "FAIL",
            "note": "CSV checks only; Databricks is not connected yet."
        }

    except Exception as e:
        return {"status": "FAIL", "error": str(e)}
