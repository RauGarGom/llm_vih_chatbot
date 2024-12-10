import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel, Field
import psycopg2 #type: ignore
from psycopg2.extras import RealDictCursor #type: ignore
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from model import vih_chat_usuario, vih_chat_profesional
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uvicorn



load_dotenv()

DB_CONFIG = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}

class FormularioRequest(BaseModel):
    id_sesion: str
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
    id_sesion: str
    municipio_residencia: str
    ccaa: str
    ambito_laboral: str
    especialidad: str
    vih_usuario: str
    vih_diagnostico: str
    vih_tratamiento: str
    ha_tratado_vih: str
    como_conocio_felgtbi: str

class ChatbotUserRequest(BaseModel):
    pregunta_usuario: str
    municipio: str
    ccaa: str
    conocer_felgtbi: str
    vih_usuario: str
    vih_diagnostico: str
    vih_tratamiento: str
    us_edad: int
    us_pais_origen: str
    us_genero: str
    us_orientacion: str
    us_situacion_afectiva: str
    us_hablado: str

class ChatbotProRequest(BaseModel):
    pregunta_profesional: str
    municipio: str
    ccaa: str
    conocer_felgtbi: str
    vih_usuario: str
    vih_diagnostico: str
    vih_tratamiento: str
    pro_ambito: str
    pro_especialidad: str
    pro_vih_profesional: str

def get_db_connection():
    conn = psycopg2.connect(
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
    )
    return conn
    
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir cualquier origen
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, DELETE, etc.)
    allow_headers=["*"],  # Permitir todas las cabeceras
)

@app.get('/')
async def home():
    return "Backend FELGTBI. v1.2. Consulta docs para las llamadas de la API"


@app.post("/respuesta-usuario")
def insertar_respuesta(formulario: FormularioRequest, request: Request):
    client = request.client
    ip = client.host if client else "0.0.0.0"

    conn = get_db_connection()
    cursor = conn.cursor()

    try:

        query = """
            INSERT INTO respuestas_usuarios (
                direccion_ip, id_sesion, tipo_usuario, municipio, ccaa, conocer_felgtbi, vih_usuario, vih_diagnostico,
                vih_tratamiento, us_edad, us_pais_origen, us_genero, us_orientacion, us_situacion_afectiva,
                us_hablado
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """
        
        valores = (
            ip,
            formulario.id_sesion,
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
                direccion_ip, id_sesion, tipo_usuario, municipio, ccaa, conocer_felgtbi, vih_usuario, vih_diagnostico,
                vih_tratamiento, pro_ambito, pro_especialidad, pro_vih_profesional
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """
        
        # Recoger los datos del formulario para insertar en la base de datos
        valores = (
            ip, 
            formulario.id_sesion, 
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



@app.post('/chatbot_usuario')
async def chatbot_usuario(data:ChatbotUserRequest,request: Request):
    ip = request.client.host if request.client else "0.0.0.0"  
    try:
        respuesta_chat = vih_chat_usuario(ip,data.pregunta_usuario,data.municipio, data.ccaa, data.conocer_felgtbi, data.vih_usuario, data.vih_diagnostico,
                data.vih_tratamiento, data.us_edad, data.us_pais_origen, data.us_genero, data.us_orientacion, data.us_situacion_afectiva,
                data.us_hablado)
        return {"status": "success", "respuesta_chat": respuesta_chat}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar una respuesta: {e}")

@app.post('/chatbot_profesional')
async def chatbot_profesional(data:ChatbotProRequest,request: Request):
    ip = request.client.host if request.client else "0.0.0.0"
    try:
        respuesta_chat = vih_chat_profesional(ip,data.pregunta_profesional,data.municipio, data.ccaa, data.conocer_felgtbi, data.vih_usuario, data.vih_diagnostico,
                data.vih_tratamiento, data.pro_ambito, data.pro_especialidad, data.pro_vih_profesional)
        return {"status": "success", "respuesta_chat": respuesta_chat}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar una respuesta: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
