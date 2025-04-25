from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import crud, schemas, database
from security import get_current_koc, get_current_ogrenci

router = APIRouter()

@router.post("/odev", response_model=schemas.Odev)
def create_odev(
    odev: schemas.OdevCreate,
    db: Session = Depends(database.get_db),
    current_koc_id: int = Depends(get_current_koc)
):
    return crud.create_odev(db=db, odev=odev)

@router.get("/odevler", response_model=List[schemas.Odev])
def read_odevler(
    skip: int = 0,
    limit: int = 100,
    koc_id: int = None,
    ogrenci_id: int = None,
    db: Session = Depends(database.get_db)
):
    odevler = crud.get_odevler(db, skip=skip, limit=limit, koc_id=koc_id, ogrenci_id=ogrenci_id)
    return odevler

@router.get("/odev/{odev_id}", response_model=schemas.Odev)
def read_odev(odev_id: int, db: Session = Depends(database.get_db)):
    db_odev = crud.get_odev(db, odev_id=odev_id)
    if db_odev is None:
        raise HTTPException(status_code=404, detail="Ödev bulunamadı")
    return db_odev

@router.put("/odev/{odev_id}", response_model=schemas.Odev)
def update_odev(
    odev_id: int,
    odev: schemas.OdevUpdate,
    db: Session = Depends(database.get_db),
    current_koc_id: int = Depends(get_current_koc)
):
    db_odev = crud.get_odev(db, odev_id=odev_id)
    if db_odev is None:
        raise HTTPException(status_code=404, detail="Ödev bulunamadı")
    if db_odev.koc_id != current_koc_id:
        raise HTTPException(status_code=403, detail="Bu işlem için yetkiniz yok")
    return crud.update_odev(db=db, odev_id=odev_id, odev=odev)

@router.delete("/odev/{odev_id}", response_model=schemas.Odev)
def delete_odev(
    odev_id: int,
    db: Session = Depends(database.get_db),
    current_koc_id: int = Depends(get_current_koc)
):
    db_odev = crud.get_odev(db, odev_id=odev_id)
    if db_odev is None:
        raise HTTPException(status_code=404, detail="Ödev bulunamadı")
    if db_odev.koc_id != current_koc_id:
        raise HTTPException(status_code=403, detail="Bu işlem için yetkiniz yok")
    return crud.delete_odev(db=db, odev_id=odev_id) 