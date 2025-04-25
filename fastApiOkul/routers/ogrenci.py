from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import schemas, crud, database
from security import get_current_koc, get_current_ogrenci, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, verify_password
from typing import List
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

@router.post("/ogrenci/login", response_model=schemas.Token)
def ogrenci_login(ogrenci_data: schemas.OgrenciLogin, db: Session = Depends(database.get_db)):
    ogrenci = crud.get_ogrenci_by_no(db, ogrenci_no=ogrenci_data.ogrenci_no)
    if not ogrenci:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Öğrenci numarası veya şifre hatalı"
        )
    if not verify_password(ogrenci_data.sifre, ogrenci.sifre_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Öğrenci numarası veya şifre hatalı"
        )
    access_token = create_access_token(data={"sub": str(ogrenci.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/ogrenci", response_model=schemas.Ogrenci)
def create_ogrenci(ogrenci: schemas.OgrenciCreate, db: Session = Depends(database.get_db)):
    db_ogrenci = crud.get_ogrenci_by_no(db, ogrenci_no=ogrenci.ogrenci_no)
    if db_ogrenci:
        raise HTTPException(status_code=400, detail="Öğrenci numarası zaten kayıtlı")
    return crud.create_ogrenci(db=db, ogrenci=ogrenci)

@router.get("/ogrenciler", response_model=List[schemas.Ogrenci])
def read_ogrenciler(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    ogrenciler = crud.get_ogrenciler(db, skip=skip, limit=limit)
    return ogrenciler

@router.get("/ogrenci/{ogrenci_id}", response_model=schemas.Ogrenci)
def read_ogrenci(ogrenci_id: int, db: Session = Depends(database.get_db)):
    db_ogrenci = crud.get_ogrenci(db, ogrenci_id=ogrenci_id)
    if db_ogrenci is None:
        raise HTTPException(status_code=404, detail="Öğrenci bulunamadı")
    return db_ogrenci

@router.put("/ogrenci/{ogrenci_id}", response_model=schemas.Ogrenci)
def update_ogrenci(
    ogrenci_id: int,
    ogrenci: schemas.OgrenciCreate,
    db: Session = Depends(database.get_db),
    current_ogrenci_id: int = Depends(get_current_ogrenci)
):
    if ogrenci_id != current_ogrenci_id:
        raise HTTPException(status_code=403, detail="Bu işlem için yetkiniz yok")
    db_ogrenci = crud.update_ogrenci(db=db, ogrenci_id=ogrenci_id, ogrenci=ogrenci)
    if db_ogrenci is None:
        raise HTTPException(status_code=404, detail="Öğrenci bulunamadı")
    return db_ogrenci

@router.delete("/ogrenci/{ogrenci_id}", response_model=schemas.Ogrenci)
def delete_ogrenci(
    ogrenci_id: int,
    db: Session = Depends(database.get_db),
    current_ogrenci_id: int = Depends(get_current_ogrenci)
):
    if ogrenci_id != current_ogrenci_id:
        raise HTTPException(status_code=403, detail="Bu işlem için yetkiniz yok")
    db_ogrenci = crud.delete_ogrenci(db=db, ogrenci_id=ogrenci_id)
    if db_ogrenci is None:
        raise HTTPException(status_code=404, detail="Öğrenci bulunamadı")
    return db_ogrenci

@router.post("/odev", response_model=schemas.Odev)
def create_odev(
    odev: schemas.OdevCreate,
    db: Session = Depends(database.get_db),
    current_ogrenci_id: int = Depends(get_current_ogrenci)
):
    return crud.create_odev(db=db, odev=odev)

@router.get("/odev/{odev_id}", response_model=schemas.OdevResponse)
def get_odev(
    odev_id: int,
    db: Session = Depends(database.get_db),
    current_koc_id: int = Depends(get_current_koc)
):
    """Ödev detaylarını getirir"""
    odev = crud.get_odev_by_id(db, odev_id)
    if not odev:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ödev bulunamadı"
        )
    if odev.koc_id != current_koc_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu ödevi görüntüleme yetkiniz yok"
        )
    return odev

@router.get("/ogrenci/odevler", response_model=List[schemas.OdevResponse])
def get_ogrenci_odevler(
    db: Session = Depends(database.get_db),
    current_ogrenci: int = Depends(get_current_ogrenci)
):
    """Öğrencinin ödevlerini listeler"""
    ogrenci = crud.get_ogrenci_by_no(db, current_ogrenci)
    if not ogrenci:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Öğrenci bulunamadı"
        )
    return crud.get_ogrenci_odevler(db, ogrenci.id)

@router.get("/koc-odevler", response_model=List[schemas.OdevResponse])
def get_koc_odevler(
    db: Session = Depends(database.get_db),
    current_koc: int = Depends(get_current_koc)
):
    """Koçun verdiği ödevleri listeler"""
    return crud.get_koc_odevler(db, current_koc)

@router.put("/odev/{odev_id}", response_model=schemas.OdevResponse)
def update_odev_durumu(
    odev_id: int,
    odev_update: schemas.OdevUpdate,
    db: Session = Depends(database.get_db),
    current_ogrenci: int = Depends(get_current_ogrenci)
):
    """Öğrenci ödev durumunu günceller"""
    odev = crud.get_odev_by_id(db, odev_id)
    if not odev:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ödev bulunamadı"
        )
    
    # Ödevin bu öğrenciye ait olduğunu kontrol et
    ogrenci = crud.get_ogrenci_by_no(db, current_ogrenci)
    if odev.ogrenci_id != ogrenci.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu ödevi güncelleme yetkiniz yok"
        )
    
    return crud.update_odev_durumu(db, odev_id, odev_update) 