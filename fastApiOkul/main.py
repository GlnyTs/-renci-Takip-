import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from database import engine, Base
from routers import koc, ogrenci, odev

# Veritabanı tablolarını oluştur
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Okul API",
    description="Okul Yönetim Sistemi API'si - Önce /api/login endpoint'inden token alın",
    version="1.0.0"
)

# 🔥 Hata Loglama Middleware'i
@app.middleware("http")
async def log_requests(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logging.error(f"🔥 HATA: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"message": f"Internal Server Error: {str(e)}"},
        )

# Routerları ekle
app.include_router(koc.router, prefix="/api", tags=["Koç"])
app.include_router(ogrenci.router, prefix="/api", tags=["Öğrenci"])
app.include_router(odev.router, prefix="/api", tags=["Ödev"])
