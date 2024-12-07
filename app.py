from fastapi import FastAPI, HTTPException
from model import vih_chat_usuario
from pydantic import BaseModel

import uvicorn

app = FastAPI()

class ChatbotRequest(BaseModel):
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

app = FastAPI()
@app.get('/')
async def home():
    return "Test API. Si ves esto, funciona!"

@app.get('/chatbot_usuario')
async def chatbot_usuario(data:ChatbotRequest):
    try:
        respuesta_chat = vih_chat_usuario(data.pregunta_usuario,data.municipio, data.ccaa, data.conocer_felgtbi, data.vih_usuario, data.vih_diagnostico,
                data.vih_tratamiento, data.us_edad, data.us_pais_origen, data.us_genero, data.us_orientacion, data.us_situacion_afectiva,
                data.us_hablado)
        return {"status": "success", "respuesta_chat": respuesta_chat}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar una respuesta: {e}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
