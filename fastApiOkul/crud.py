from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
import models
import schemas
from security import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_current_koc, get_current_ogrenci
from passlib.context import CryptContext
from typing import List, Optional

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_koc_by_id(db: Session, koc_id: int):
    return db.query(models.Koc).filter(models.Koc.id == koc_id).first()

def create_koc(db: Session, koc: schemas.KocCreate):
    hashed_password = pwd_context.hash(koc.sifre)
    db_koc = models.Koc(
        email=koc.email,
        ad=koc.ad,
        soyad=koc.soyad,
        sifre_hash=hashed_password
    )
    db.add(db_koc)
    db.commit()
    db.refresh(db_koc)
    return db_koc

def get_koc_by_email(db: Session, email: str):
    return db.query(models.Koc).filter(models.Koc.email == email).first()

# 🟢 Öğrenci CRUD Fonksiyonları
def get_ogrenci_by_id(db: Session, ogrenci_id: int):
    return db.query(models.Ogrenci).filter(models.Ogrenci.id == ogrenci_id).first()

def get_ogrenci(db: Session, ogrenci_id: int):
    return db.query(models.Ogrenci).filter(models.Ogrenci.id == ogrenci_id).first()

def get_ogrenci_by_email(db: Session, email: str):
    return db.query(models.Ogrenci).filter(models.Ogrenci.email == email).first()

def get_ogrenci_by_no(db: Session, ogrenci_no: str):
    return db.query(models.Ogrenci).filter(models.Ogrenci.ogrenci_no == ogrenci_no).first()

def get_ogrenciler(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Ogrenci).offset(skip).limit(limit).all()

def create_ogrenci(db: Session, ogrenci: schemas.OgrenciCreate):
    hashed_password = pwd_context.hash(ogrenci.sifre)
    db_ogrenci = models.Ogrenci(
        ogrenci_no=ogrenci.ogrenci_no,
        ad=ogrenci.ad,
        soyad=ogrenci.soyad,
        email=ogrenci.email,
        sifre_hash=hashed_password
    )
    db.add(db_ogrenci)
    db.commit()
    db.refresh(db_ogrenci)
    return db_ogrenci

def update_ogrenci(db: Session, ogrenci_id: int, ogrenci: schemas.OgrenciCreate):
    db_ogrenci = get_ogrenci(db, ogrenci_id)
    if db_ogrenci:
        for key, value in ogrenci.dict(exclude_unset=True).items():
            if key == "sifre":
                value = get_password_hash(value)
            setattr(db_ogrenci, key, value)
        db.commit()
        db.refresh(db_ogrenci)
    return db_ogrenci

def delete_ogrenci(db: Session, ogrenci_id: int):
    db_ogrenci = get_ogrenci(db, ogrenci_id)
    if db_ogrenci:
        db.delete(db_ogrenci)
        db.commit()
    return db_ogrenci

# Koç-Öğrenci ilişkisi için fonksiyonlar
def get_atanmamis_ogrenciler(db: Session):
    """Hiçbir koça atanmamış öğrencileri getirir"""
    return db.query(models.Ogrenci).filter(~models.Ogrenci.koclar.any()).all()

def get_koc_ogrencileri(db: Session, koc_id: int):
    """Bir koçun öğrencilerini getirir"""
    koc = get_koc_by_id(db, koc_id)
    if not koc:
        return []
    return koc.ogrenciler

def koc_ogrenci_ekle(db: Session, koc_id: int, ogrenci_id: int):
    """Bir koça öğrenci ekler"""
    koc = get_koc_by_id(db, koc_id)
    ogrenci = get_ogrenci_by_id(db, ogrenci_id)
    
    if not koc or not ogrenci:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Koç veya öğrenci bulunamadı"
        )
    
    # Öğrenci zaten koçun öğrencisi mi kontrol et
    if ogrenci in koc.ogrenciler:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu öğrenci zaten koçun öğrencisi"
        )
    
    koc.ogrenciler.append(ogrenci)
    db.commit()
    return koc

def koc_ogrenci_cikar(db: Session, koc_id: int, ogrenci_id: int):
    """Bir koçtan öğrenci çıkarır"""
    koc = get_koc_by_id(db, koc_id)
    ogrenci = get_ogrenci_by_id(db, ogrenci_id)
    
    if not koc or not ogrenci:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Koç veya öğrenci bulunamadı"
        )
    
    # Öğrenci koçun öğrencisi mi kontrol et
    if ogrenci not in koc.ogrenciler:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu öğrenci koçun öğrencisi değil"
        )
    
    koc.ogrenciler.remove(ogrenci)
    db.commit()
    return koc

# 🟢 Ödev CRUD İşlemleri
def create_odev(db: Session, odev: schemas.OdevCreate):
    db_odev = models.Odev(**odev.dict())
    db.add(db_odev)
    db.commit()
    db.refresh(db_odev)
    return db_odev

def get_odev(db: Session, odev_id: int):
    return db.query(models.Odev).filter(models.Odev.id == odev_id).first()

def get_ogrenci_odevler(db: Session, ogrenci_id: int):
    return db.query(models.Odev).filter(models.Odev.ogrenci_id == ogrenci_id).all()

def get_koc_odevler(db: Session, koc_id: int):
    return db.query(models.Odev).filter(models.Odev.koc_id == koc_id).all()

def update_odev_tamamlandi(db: Session, odev_id: int, tamamlandi: bool):
    db_odev = get_odev(db, odev_id)
    if db_odev:
        db_odev.tamamlandi = tamamlandi
        db.commit()
        db.refresh(db_odev)
    return db_odev

def get_odevler(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    koc_id: Optional[int] = None,
    ogrenci_id: Optional[int] = None
):
    query = db.query(models.Odev)
    if koc_id:
        query = query.filter(models.Odev.koc_id == koc_id)
    if ogrenci_id:
        query = query.filter(models.Odev.ogrenci_id == ogrenci_id)
    return query.offset(skip).limit(limit).all()

def get_ogrenci_odevleri(db: Session, ogrenci_id: int):
    return db.query(models.Odev).filter(models.Odev.ogrenci_id == ogrenci_id).all()

def get_koc_odevleri(db: Session, koc_id: int):
    return db.query(models.Odev).filter(models.Odev.koc_id == koc_id).all()

def update_odev(db: Session, odev_id: int, odev: schemas.OdevUpdate):
    db_odev = get_odev(db, odev_id)
    if db_odev:
        for key, value in odev.dict(exclude_unset=True).items():
            setattr(db_odev, key, value)
        db.commit()
        db.refresh(db_odev)
    return db_odev

def delete_odev(db: Session, odev_id: int):
    db_odev = get_odev(db, odev_id)
    if db_odev:
        db.delete(db_odev)
        db.commit()
    return db_odev 