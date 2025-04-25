from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean, Table
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

# Koç-Öğrenci ilişki tablosu
koc_ogrenci = Table(
    "koc_ogrenci",
    Base.metadata,
    Column("koc_id", Integer, ForeignKey("koclar.id"), primary_key=True),
    Column("ogrenci_id", Integer, ForeignKey("ogrenciler.id"), primary_key=True)
)

# 🟢 Koç Modeli
class Koc(Base):
    __tablename__ = "koclar"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    ad = Column(String)
    soyad = Column(String)
    sifre_hash = Column(String)
    odevler = relationship("Odev", back_populates="koc")
    ogrenciler = relationship("Ogrenci", secondary=koc_ogrenci, back_populates="koclar")

# 🟢 Öğrenci Modeli
class Ogrenci(Base):
    __tablename__ = "ogrenciler"

    id = Column(Integer, primary_key=True, index=True)
    ogrenciNo = Column(String, unique=True, index=True)
    ad = Column(String)
    soyad = Column(String)
    email = Column(String, unique=True, index=True)
    sifre_hash = Column(String)
    koc_id = Column(Integer, ForeignKey("koclar.id"), nullable=True)
    
    koc = relationship("Koc", back_populates="ogrenciler")
    odevler = relationship("Odev", back_populates="ogrenci")

class Odev(Base):
    __tablename__ = "odevler"
    
    id = Column(Integer, primary_key=True, index=True)
    baslik = Column(String)
    aciklama = Column(Text)
    teslim_tarihi = Column(DateTime)
    olusturma_tarihi = Column(DateTime, default=datetime.utcnow)
    durum = Column(String, default="Beklemede")  # Beklemede, Tamamlandı, İptal
    notlar = Column(Text, nullable=True)
    
    koc_id = Column(Integer, ForeignKey("koclar.id"))
    ogrenci_id = Column(Integer, ForeignKey("ogrenciler.id"))
    
    koc = relationship("Koc", back_populates="odevler")
    ogrenci = relationship("Ogrenci", back_populates="odevler")
