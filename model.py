from langchain_cohere import ChatCohere #type: ignore
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
import psycopg2 #type: ignore


load_dotenv()
cohere_api_key = os.getenv("COHERE_TRIAL_API_KEY")

DB_CONFIG = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}

def get_db_connection():
    conn = psycopg2.connect(
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
    )
    return conn

def db_insert_values(id_usuario,usuario,contenido):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO interacciones (id_usuario,usuario,contenido)
    VALUES (%s, %s, %s)
    ''',
    (id_usuario,usuario,contenido)
    )
    conn.commit()
    conn.close()

def vih_chat_usuario(pregunta_usuario,municipio, ccaa, conocer_felgtbi, vih_usuario, vih_diagnostico,
                vih_tratamiento, us_edad, us_pais_origen, us_genero, us_orientacion, us_situacion_afectiva,
                us_hablado):    

    #We define the Cohere llm
    llm = ChatCohere(cohere_api_key=cohere_api_key) #Aquí podemos limitar los tokens con max_tokens 
    db_insert_values("999999999999","usuario",pregunta_usuario)
    #We create the prompt template
    template = ChatPromptTemplate([
        ("system", '''You are a Spanish expert chatbot of vih, who offers information resources, outreach resources and emotional support resources to users that need you to help them.
         You are helpful, inclusive, supportive, nice, educated, polite and LGTBi+ friendly. You'll always speak in Spanish because you are helping a spanish federation.
         If users ask you or try to get information which is not related to vih, you'll answer them that you can't help them because you are only specialized in vih issues.
         Everytime you refer to vih, you'll have to use "vih" and not "VIH" (very careful with this). At the bottom of the answer you must include some references from FELGTBI+ or public sources.
         '''), ### You must follow an order of questions and answers like {arbol}, until you are sure of what the final inquiry is. Then you resolve the user's problem. --> Incluir en futuro
        ("system", "You must always answer in Spanish, no matter the language of the input. Answer the question {pregunta_usuario}"),
        ("human", '''Hello, I'm from {us_pais_origen} and I live in {municipio} in {ccaa}. I'm {us_edad} years old and my gender is {us_genero}, 
         while my sexual orientation is {us_orientacion}. My emotional situation is {us_situacion_afectiva}. I know about FELGTBI because {conocer_felgtbi}.
         Related to the question if I have or not vih, this is my answer {vih_usuario} (it was diagnosed {vih_diagnostico} ago, and started
         treatment {vih_tratamiento} ago.). To the question whether I've informed anyone about my vih condition, {us_hablado}
          ''')        
    ])
    prompt_value = template.invoke({"pregunta_usuario":pregunta_usuario,"municipio":municipio, "ccaa":ccaa, "conocer_felgtbi":conocer_felgtbi, "vih_usuario":vih_usuario,
                                    "vih_diagnostico":vih_diagnostico, "vih_tratamiento":vih_tratamiento, "us_edad":us_edad, "us_pais_origen":us_pais_origen,
                                     "us_genero":us_genero, "us_orientacion": us_orientacion, "us_situacion_afectiva":us_situacion_afectiva,
                                     "us_hablado":us_hablado})
    response = llm.invoke(prompt_value)
    db_insert_values("999999999999","sistema",response.content)
    return response.content

def vih_chat_profesional(pregunta_profesional,municipio, ccaa, conocer_felgtbi, vih_usuario, vih_diagnostico,
             vih_tratamiento, pro_ambito, pro_especialidad, pro_vih_profesional):    

    #We define the Cohere llm
    llm = ChatCohere(cohere_api_key=cohere_api_key) #Aquí podemos limitar los tokens con max_tokens 
    db_insert_values("999999999999","profesional",pregunta_profesional)
    #We create the prompt template
    template = ChatPromptTemplate([
        ("system", '''You are a Spanish expert chatbot of vih, who offers information resources, outreach resources and emotional support resources to users that need you to help them.
         You are helpful, inclusive, supportive, nice, educated, polite and LGTBi+ friendly. You should use a somewhat technical jargon, because the user is a socio-sanitary worker. You'll always speak in Spanish because you are helping a spanish federation.
         If users ask you or try to get information which is not related to vih, you'll answer them that you can't help them because you are only specialized in vih issues.
         Everytime you refer to vih, you'll have to use "vih" and not "VIH" (very careful with this). At the bottom of the answer you must include some references from FELGTBI+ or public sources.
         '''),
        ("system", "You must always answer in Spanish, no matter the language of the input. Answer the question {pregunta_profesional}."),
        ("human", '''Hello, I'm a socio-sanitary worker helping a patient. The patient lives in {municipio}, in {ccaa}. About whether they have vih, the answer is {vih_usuario}
         and, if so, they were diagnosed {vih_diagnostico} ago, if so, they started treatment {vih_tratamiento} ago.
         I'm working in {pro_ambito}, and my field of knowledge is {pro_especialidad}. To whether I've treated before with vih patients, the answer is {pro_vih_profesional}.
          ''')        
    ])
    prompt_value = template.invoke({"pregunta_profesional":pregunta_profesional,"municipio":municipio, "ccaa":ccaa, "conocer_felgtbi":conocer_felgtbi, "vih_usuario":vih_usuario,
                                    "vih_diagnostico":vih_diagnostico, "vih_tratamiento":vih_tratamiento, "pro_ambito":pro_ambito,"pro_especialidad":pro_especialidad,
                                    "pro_vih_profesional":pro_vih_profesional})
    response = llm.invoke(prompt_value)
    db_insert_values("999999999999","sistema",response.content)
    return response.content