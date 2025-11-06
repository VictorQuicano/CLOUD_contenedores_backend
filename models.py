from sqlalchemy import create_engine, Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

Base = declarative_base()



class User(Base):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True, index=True)

class ListeningRecord(Base):
    __tablename__ = "listening_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    song = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


class Cancion(Base):
    __tablename__ = "tracks"
    id = Column(String, primary_key=True, index=True)
    artist = Column(String)
    song = Column(String)
    album_name = Column(String)

# Modelos Pydantic
class CancionResponse(BaseModel):
    id: str
    artist: str
    song: str
    album_name: str
    timestamp: datetime

    class Config:
        from_attributes = True

class UserStatsResponse(BaseModel):
    user_id: str
    ultimas_5_canciones: List[CancionResponse]
    total_canciones_escuchadas: int
    dia_mas_escuchado: Optional[str]

class CreateListeningRequest(BaseModel):
    user_id: str
    track_id: str

class CreateListeningRandomRequest(BaseModel):
    user_id: str

class TopCancionStats(BaseModel):
    id: str
    artist: str
    song: str
    album_name: Optional[str] = None
    veces_escuchada: Optional[int] = None
    timestamp: Optional[datetime] = None

class TopUsuarioStats(BaseModel):
    user_id: str
    total_registros: int
    primera_escucha: Optional[datetime] = None
    ultima_escucha: Optional[datetime] = None
    rango_fechas: Optional[str] = None

class StatsResponse(BaseModel):
    total_usuarios: int
    canciones_mas_escuchadas: List[TopCancionStats]
    canciones_mas_actuales: List[TopCancionStats]
    top_usuarios: List[TopUsuarioStats]

    class Config:
        from_attributes = True