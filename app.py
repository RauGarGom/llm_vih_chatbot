import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel, Field
import psycopg2 #type: ignore
from psycopg2.extras import RealDictCursor #type: ignore
from pydantic import BaseModel
import uvicorn

app = FastAPI()

load_dotenv()

DB_CONFIG = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}

class FormularioRequest(BaseModel):
    edad: int = Field(..., gt=0, description="Edad del usuario (mayor a 0)")
    pais_origen: str
    ccaa: str
    municipio_residencia: str
    genero: str
    orientacion_sexual: str
    situacion_afectiva: str
    tiene_vih: str
    fecha_diagnostico: str
    fecha_inicio_tratamiento: str
    hablado_con_alguien: str
    como_conocio_felgtbi: str

class FormularioProfesionalRequest(BaseModel):
    municipio_residencia: str
    ccaa: str
    ambito_laboral: str
    especialidad: str
    vih_usuario: str
    vih_diagnostico: str
    vih_tratamiento: str
    ha_tratado_vih: str
    como_conocio_felgtbi: str

def get_db_connection():
    conn = psycopg2.connect(
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
    )
    return conn
    

@app.post("/respuesta-usuario")
def insertar_respuesta(formulario: FormularioRequest, request: Request):
    client = request.client
    ip = client.host if client else "0.0.0.0"

    conn = get_db_connection()
    cursor = conn.cursor()

    try:

        query = """
            INSERT INTO respuestas_usuarios (
                direccion_ip, tipo_usuario, municipio, ccaa, conocer_felgtbi, vih_usuario, vih_diagnostico,
                vih_tratamiento, us_edad, us_pais_origen, us_genero, us_orientacion, us_situacion_afectiva,
                us_hablado
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """
        
        valores = (
            ip,
            "usuario",
            formulario.municipio_residencia,
            formulario.ccaa,
            formulario.como_conocio_felgtbi,
            formulario.tiene_vih, 
            formulario.fecha_diagnostico, 
            formulario.fecha_inicio_tratamiento,
            formulario.edad, 
            formulario.pais_origen,
            formulario.genero,
            formulario.orientacion_sexual,
            formulario.situacion_afectiva,
            formulario.hablado_con_alguien, 
        )
        

        cursor.execute(query, valores)
        conn.commit()
        return {"status": "success", "message": "Datos insertados correctamente."}
    
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al insertar los datos: {e}")
    
    finally:
        cursor.close()
        conn.close()


@app.post("/respuesta-profesional")
async def insertar_respuesta_profesional(formulario: FormularioProfesionalRequest, request: Request):
    # Obtener la dirección IP del usuario
    ip = request.client.host if request.client else "0.0.0.0"  

    # Establecer la conexión con la base de datos
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Consulta SQL para insertar los datos en la base de datos
        query = """
            INSERT INTO respuestas_usuarios (
                direccion_ip, tipo_usuario, municipio, ccaa, conocer_felgtbi, vih_usuario, vih_diagnostico,
                vih_tratamiento, pro_ambito, pro_especialidad, pro_vih_profesional
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """
        
        # Recoger los datos del formulario para insertar en la base de datos
        valores = (
            ip,  
            "sociosanitario",
            formulario.municipio_residencia,  
            formulario.ccaa,  
            formulario.como_conocio_felgtbi,  
            formulario.vih_usuario, 
            formulario.vih_diagnostico,  
            formulario.vih_tratamiento, 
            formulario.ambito_laboral,  
            formulario.especialidad,  
            formulario.ha_tratado_vih, 
        )

        cursor.execute(query, valores)
        conn.commit()

        return {"status": "success", "message": "Datos insertados correctamente."}
    
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al insertar los datos: {e}")
    
    finally:
        cursor.close()
        conn.close()


@app.get('/')
async def home():
    return "Test API. Si ves esto, funciona!"

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
