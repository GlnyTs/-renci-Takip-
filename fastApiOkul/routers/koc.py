from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import crud, schemas, database
from security import get_current_koc, create_access_token, verify_password

router = APIRouter()

@router.post("/koc/login", response_model=schemas.Token)
def koc_login(koc_data: schemas.KocLogin, db: Session = Depends(database.get_db)):
    koc = crud.get_koc_by_email(db, email=koc_data.email)
    if not koc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email veya şifre hatalı"
        )
    if not verify_password(koc_data.sifre, koc.sifre_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email veya şifre hatalı"
        )
    access_token = create_access_token(data={"sub": str(koc.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/koc", response_model=schemas.Koc)
def create_koc(koc: schemas.KocCreate, db: Session = Depends(database.get_db)):
    db_koc = crud.get_koc_by_email(db, email=koc.email)
    if db_koc:
        raise HTTPException(status_code=400, detail="Email zaten kayıtlı")
    return crud.create_koc(db=db, koc=koc)

@router.get("/koclar", response_model=List[schemas.Koc])
def read_koclar(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    koclar = crud.get_koclar(db, skip=skip, limit=limit)
    return koclar

@router.get("/koc/{koc_id}", response_model=schemas.Koc)
def read_koc(koc_id: int, db: Session = Depends(database.get_db)):
    db_koc = crud.get_koc(db, koc_id=koc_id)
    if db_koc is None:
        raise HTTPException(status_code=404, detail="Koç bulunamadı")
    return db_koc

@router.put("/koc/{koc_id}", response_model=schemas.Koc)
def update_koc(
    koc_id: int,
    koc: schemas.KocCreate,
    db: Session = Depends(database.get_db),
    current_koc_id: int = Depends(get_current_koc)
):
    if koc_id != current_koc_id:
        raise HTTPException(status_code=403, detail="Bu işlem için yetkiniz yok")
    db_koc = crud.update_koc(db=db, koc_id=koc_id, koc=koc)
    if db_koc is None:
        raise HTTPException(status_code=404, detail="Koç bulunamadı")
    return db_koc

@router.delete("/koc/{koc_id}", response_model=schemas.Koc)
def delete_koc(
    koc_id: int,
    db: Session = Depends(database.get_db),
    current_koc_id: int = Depends(get_current_koc)
):
    if koc_id != current_koc_id:
        raise HTTPException(status_code=403, detail="Bu işlem için yetkiniz yok")
    db_koc = crud.delete_koc(db=db, koc_id=koc_id)
    if db_koc is None:
        raise HTTPException(status_code=404, detail="Koç bulunamadı")
    return db_koc