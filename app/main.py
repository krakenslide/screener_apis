from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from app.services import generate_excel

app = FastAPI(
    title="Screener Data Export API",
    description="An API to fetch data from Screener.in and export it as an Excel file.",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend's URL (e.g., ["http://localhost:3000"])
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

@app.get("/health", summary="Health Check", tags=["Health"])
def health_check():
    """
    Health check endpoint to verify if the server is running.
    """
    return JSONResponse(content={"status": "UP", "message": "Server is running."})

@app.get("/export-excel", summary="Export Screener data to Excel", tags=["Data Export"])
def export_excel():
    try:
        excel_file = generate_excel()
        if not excel_file:
            return JSONResponse(content={"status": "ERROR", "message": "Failed to fetch data or tables are empty."}, status_code=500)

        return StreamingResponse(
            content=excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=merged_screener_data.xlsx"}
        )
    except Exception as e:
        return JSONResponse(content={"status": "ERROR", "message": str(e)}, status_code=500)
