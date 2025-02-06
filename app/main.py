from fastapi import FastAPI, Response, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.responses import JSONResponse
from app.services import generate_excel

app = FastAPI(
    title="Screener Data Export API",
    description="An API to fetch data from Screener.in and export it as an Excel file.",
    version="1.0.0",
)

@app.get("/health", summary="Health Check", tags=["Health"])
def health_check():
    """
    Health check endpoint to verify if the server is running.
    """
    return JSONResponse(content={"status": "UP", "message": "Server is running."})
@app.get("/export-excel")
def export_excel():
    try:
        excel_file = generate_excel()
        if not excel_file:
            raise HTTPException(status_code=500, detail="Failed to fetch data or tables are empty.")

        return StreamingResponse(
            content=excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=merged_screener_data.xlsx"}
        )
    except Exception as e:
        # Log the error for debugging
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
