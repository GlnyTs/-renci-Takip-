from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from enum import Enum

# 🟢 Koç Şemaları
class KocBase(BaseModel):
    email: EmailStr
    ad: str
    soyad: str
    uzmanlik: str

class KocCreate(KocBase):
    sifre: str

class Koc(KocBase):
    id: int
    created_at: datetime
    ogrenciler: List['Ogrenci'] = []

    class Config:
        from_attributes = True

class KocLogin(BaseModel):
    email: str
    sifre: str

class KocTokenData(BaseModel):
    koc_id: int | None = None

# 🟢 Öğrenci Şemaları
class OdevDurum(str, Enum):
    BEKLEMEDE = "beklemede"
    TAMAMLANDI = "tamamlandi"
    REDDEDILDI = "reddedildi"

class OgrenciBase(BaseModel):
    ad: str
    soyad: str
    email: EmailStr
    sinif: int

class OgrenciCreate(OgrenciBase):
    sifre: str

class OgrenciLogin(BaseModel):
    ogrenci_no: str
    sifre: str

class Ogrenci(OgrenciBase):
    id: int
    koc_id: Optional[int] = None
    olusturma_tarihi: datetime

    class Config:
        orm_mode = True

class OdevBase(BaseModel):
    baslik: str
    aciklama: str
    teslim_tarihi: datetime

class OdevCreate(OdevBase):
    ogrenci_id: int
    koc_id: int

class OdevUpdate(BaseModel):
    durum: OdevDurum

class Odev(OdevBase):
    id: int
    durum: OdevDurum
    olusturma_tarihi: datetime
    ogrenci_id: int
    koc_id: int

    class Config:
        orm_mode = True

class OdevResponse(Odev):
    pass

# Koç-Öğrenci ilişkisi için şemalar
class OgrenciKocEkle(BaseModel):
    ogrenci_id: int

class OgrenciKocCikar(BaseModel):
    ogrenci_id: int

class OgrenciKocListe(BaseModel):
    id: int
    ad: str
    soyad: str
    ogrenci_no: int
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    kullanici_tipi: Optional[str] = None
