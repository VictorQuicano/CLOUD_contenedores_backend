from fastapi import FastAPI, HTTPException, Depends

from sqlalchemy import create_engine, Column, Integer, String, DateTime, func, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import List, Optional

from models import *
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()

# Configuración de la base de datos
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelos SQLAlchemy

# FastAPI app
app = FastAPI(title="Music Listening API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency para obtener la sesión de DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "API de seguimiento de música"}

@app.get("/user/{user_id}/stats", response_model=UserStatsResponse)
def get_user_stats(user_id: str, db: Session = Depends(get_db)):
    """
    Obtiene las últimas 5 canciones escuchadas, total de canciones 
    y el día que más escuchó música
    """
    # Verificar que el usuario existe
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Obtener las últimas 5 canciones con información completa
    ultimas_canciones = (
        db.query(
            Cancion.id,
            Cancion.artist,
            Cancion.song,
            Cancion.album_name,
            ListeningRecord.timestamp
        )
        .join(ListeningRecord, Cancion.id == ListeningRecord.song)
        .filter(ListeningRecord.user_id == user_id)
        .order_by(ListeningRecord.timestamp.desc())
        .limit(5)
        .all()
    )
    #print(ultimas_canciones)

    # Convertir a lista de diccionarios
    canciones_list = [
        {
            "id": c[0],         # aquí
            "artist": c[1],
            "song": c[2],
            "album_name": c[3],
            "timestamp": c[4]
        }
        for c in ultimas_canciones
    ]

    

    # Contar total de canciones escuchadas
    total_canciones = (
        db.query(ListeningRecord)
        .filter(ListeningRecord.user_id == user_id)
        .count()
    )
    
    # Encontrar el día que más escuchó música
    dia_mas_escuchado = (
        db.query(
            func.date(ListeningRecord.timestamp).label('fecha'),
            func.count(ListeningRecord.id).label('cantidad')
        )
        .filter(ListeningRecord.user_id == user_id)
        .group_by(func.date(ListeningRecord.timestamp))
        .order_by(func.count(ListeningRecord.id).desc())
        .first()
    )
    
    dia_mas_escuchado_str = None
    if dia_mas_escuchado:
        dia_mas_escuchado_str = str(dia_mas_escuchado.fecha)
    
    return UserStatsResponse(
        user_id=user_id,
        ultimas_5_canciones=canciones_list,
        total_canciones_escuchadas=total_canciones,
        dia_mas_escuchado=dia_mas_escuchado_str
    )

@app.post("/listening", status_code=201)
def create_listening_record(request: CreateListeningRequest, db: Session = Depends(get_db)):
    """
    Crea un nuevo registro de escucha usando el timestamp actual
    """
    # Verificar que el usuario existe
    user = db.query(User).filter(User.user_id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Verificar que la canción existe
    cancion = db.query(Cancion).filter(Cancion.id == request.track_id).first()
    if not cancion:
        raise HTTPException(status_code=404, detail="Canción no encontrada")
    
    # Crear nuevo registro con timestamp actual
    nuevo_registro = ListeningRecord(
        user_id=request.user_id,
        song=request.track_id,
        timestamp=datetime.utcnow()
    )
    
    db.add(nuevo_registro)
    db.commit()
    db.refresh(nuevo_registro)
    
    return {
        "message": "Registro creado exitosamente",
        "user_id": nuevo_registro.user_id,
        "track_id": nuevo_registro.song,
        "timestamp": nuevo_registro.timestamp
    }

@app.post("/listening_random", status_code=201)
def create_random_listening_record(request: CreateListeningRandomRequest, db: Session = Depends(get_db)):
    """
    Crea un nuevo registro de escucha para el usuario dado,
    seleccionando una canción aleatoria de la base de datos.
    """
    # Verificar que el usuario existe
    user = db.query(User).filter(User.user_id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Seleccionar canción aleatoria
    cancion_random = db.query(Cancion).order_by(func.random()).first()
    if not cancion_random:
        raise HTTPException(status_code=404, detail="No hay canciones en la base de datos")
    
    # Crear nuevo registro con timestamp actual
    nuevo_registro = ListeningRecord(
        user_id=request.user_id,
        song=cancion_random.id,
        timestamp=datetime.utcnow()
    )
    
    db.add(nuevo_registro)
    db.commit()
    db.refresh(nuevo_registro)
    
    return {
        "message": "Registro creado exitosamente",
        "user_id": nuevo_registro.user_id,
        "track_id": nuevo_registro.song,
        "timestamp": nuevo_registro.timestamp
    }



# Endpoint adicional para verificar la conexión
@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Verifica que la conexión a la base de datos funciona"""
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)