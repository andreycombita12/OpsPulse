from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, text
from pydantic import BaseModel
from contextlib import asynccontextmanager
import database

# 1. Esquemas de validación con Pydantic
class MetricCreate(BaseModel):
    service_name: str
    status: str

class MetricResponse(MetricCreate):
    id: int

    class Config:
        from_attributes = True

# 2. Modelo de datos en SQLAlchemy (PostgreSQL)
class MetricModel(database.Base):
    __tablename__ = "metrics"
    id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String, index=True)
    status = Column(String)

# 3. Gestor de ciclo de vida de la aplicación
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        database.Base.metadata.create_all(bind=database.engine)
    except Exception as e:
        print(f"Error inicializando tablas: {e}")
    yield

# Configuración con root_path para Nginx Reverse Proxy
app = FastAPI(
    title="OpsPulse API",
    version="1.0.0",
    root_path="/api",
    lifespan=lifespan
)

# 4. Endpoints de la API
@app.get("/")
def home():
    return {"mensaje": "¡OpsPulse API activa!"}

@app.get("/health")
def health_check(db: Session = Depends(database.get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de conexión a la base de datos: {str(e)}")

# Consultar todas las métricas
@app.get("/metrics", response_model=list[MetricResponse])
def get_metrics(db: Session = Depends(database.get_db)):
    return db.query(MetricModel).all()

# Crear una nueva métrica
@app.post("/metrics", response_model=MetricResponse)
def create_metric(metric: MetricCreate, db: Session = Depends(database.get_db)):
    db_metric = MetricModel(service_name=metric.service_name, status=metric.status)
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    return db_metric

# Eliminar una métrica existente
@app.delete("/metrics/{metric_id}")
def delete_metric(metric_id: int, db: Session = Depends(database.get_db)):
    db_metric = db.query(MetricModel).filter(MetricModel.id == metric_id).first()
    
    if not db_metric:
        raise HTTPException(status_code=404, detail="Métrica no encontrada")
    
    db.delete(db_metric)
    db.commit()
    
    return {"mensaje": f"Métrica {metric_id} eliminada exitosamente"}
