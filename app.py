from fastapi import FastAPI, HTTPException
from model import vih_chat_usuario, vih_chat_profesional
from pydantic import BaseModel
import uvicorn

app = FastAPI()

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


app = FastAPI()
@app.get('/')
async def home():
    return "Test API. Si ves esto, funciona!"

@app.post('/chatbot_usuario')
async def chatbot_usuario(data:ChatbotUserRequest):
    try:
        respuesta_chat = vih_chat_usuario(data.pregunta_usuario,data.municipio, data.ccaa, data.conocer_felgtbi, data.vih_usuario, data.vih_diagnostico,
                data.vih_tratamiento, data.us_edad, data.us_pais_origen, data.us_genero, data.us_orientacion, data.us_situacion_afectiva,
                data.us_hablado)
        return {"status": "success", "respuesta_chat": respuesta_chat}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar una respuesta: {e}")

@app.post('/chatbot_profesional')
async def chatbot_profesional(data:ChatbotProRequest):
    try:
        respuesta_chat = vih_chat_profesional(data.pregunta_profesional,data.municipio, data.ccaa, data.conocer_felgtbi, data.vih_usuario, data.vih_diagnostico,
                data.vih_tratamiento, data.pro_ambito, data.pro_especialidad, data.pro_vih_profesional)
        return {"status": "success", "respuesta_chat": respuesta_chat}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar una respuesta: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
