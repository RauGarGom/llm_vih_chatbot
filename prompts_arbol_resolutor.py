#Importación de librerías
import cohere  #LLM used for the development of the application
from langchain_cohere import ChatCohere
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, Form
from langchain.prompts.few_shot import FewShotPromptTemplate #for creating prompts with few-shot examples
from langchain.prompts.prompt import PromptTemplate #for formatting the few-shot examples
from langchain.prompts import FewShotChatMessagePromptTemplate
from langchain.schema import HumanMessage, AIMessage, SystemMessage
import json
from langchain.prompts import PromptTemplate
from langchain.prompts import FewShotPromptTemplate
from langchain_cohere import ChatCohere
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
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

def db_insert_values_decisor(id_sesion, tipo_usuario, contenido, tipo_user_message, categoria_user_message, tipo_prompt):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO interacciones (id_sesion, tipo_usuario, contenido, tipo_user_message, categoria_user_message, tipo_prompt)
    VALUES (%s, %s, %s, %s, %s, %s)
    ''',
    (id_sesion, tipo_usuario, contenido, tipo_user_message, categoria_user_message, tipo_prompt)
    )
    conn.commit()
    conn.close()

def db_user_context(id_sesion):
    '''
    Función que devuelve el contexto del usuario (información del formulario cerrado)
    para el que tenemos su id_sesión
    '''
    conn = get_db_connection()
    cursor = conn.cursor()
    # query = ''' SELECT * FROM respuestas_usuarios '''
    cursor.execute('''
        SELECT *
        FROM respuestas_usuarios
        WHERE id_sesion = %s
        ORDER BY id_respuesta_usuario DESC LIMIT 1
        ''', (id_sesion,))
    desc = cursor.description
    column_names = [col[0] for col in desc]
    data = [dict(zip(column_names, row))  
            for row in cursor.fetchall()]
    conn.close()
    return data[0]

def db_user_interaction(id_sesion):
    '''
    Función que devuelve la interacción del usuario para el que tenemos su id_sesión
    '''
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT *
        FROM interacciones
        WHERE id_sesion = %s and tipo_usuario != 'sistema' and tipo_user_message = 'cerrada'
        ''', (id_sesion,))
    desc = cursor.description
    column_names = [col[0] for col in desc]
    data = [dict(zip(column_names, row))  
            for row in cursor.fetchall()]
    conn.close()
    return data[0]

def model_resolutor(id_sesion):
    '''
    Función que devuelve el recurso para el usuario asociado a la sesión 'id_sesion', es decir,
    devuelve la respuesta del llm final
    '''    
    #We define the Cohere llm
    llm = ChatCohere(cohere_api_key=cohere_api_key, temperature=0, model="command-r") 
    #Obtenemos el contexto del usuario
    context = db_user_context(id_sesion)
    #Obtenemos la interacción cerrada del usuario
    interaction = db_user_interaction(id_sesion)
    
    #We create the prompt template
    template = ChatPromptTemplate([
        ("system", '''You are a Spanish expert chatbot of vih who offers resources to users that need you to help them. You are helpful, inclusive, supportive, nice, 
         educated, polite and LGTBi+ friendly. You'll always speak in Spanish because you are a member of a spanish federation. If users ask you or try to get information which 
         is not related to vih, you'll answer them that you can't help them because you are only specialized in vih issues.
         Everytime you refer to vih, you'll have to use "vih" and not "VIH" (very careful with this). You must include some references of the resources that you
         provide to the users from FELGTBI+ or public but trustful sources (including links to the correspondant services)
         - If {tipo_usuario} is 'usuario' you will give them the sources of {categoria_user_message} for his doubt {contenido}, taking into account that:
            - He lives in {municipio} in {ccaa}
            - He is from {us_pais_origen}
            - He knows about FELGTBI+ because {conocer_felgtbi}
            - Related to the question if he has or not vih, this is his answer {vih_usuario} (it was diagnosed {vih_diagnostico} ago, and started
            treatment {vih_tratamiento} ago.). To the question whether he has informed anyone about his vih condition, {us_hablado}
            - His sexual orientation is {us_orientacion}
            - His gender is {us_genero}
            - His affective situation is {us_situacion_afectiva}
         - Nevertheles, if {tipo_usuario} is 'sociosanitario' you will give them the sources of {categoria_user_message} for his doubt {contenido}, taking into account that:
            - His work sphere is {pro_ambito}
            - His speciality is {pro_especialidad}
            - He has {pro_vih_profesional} worked with other patients with vih
            - He knows about FELGTBI+ because {conocer_felgtbi}
         '''),
         ("human", '''Hello, I'm {tipo_usuario}. I need {categoria_user_message} sources for my doubt {contenido}.
          ''')        
    ])

    prompt_value = template.invoke({"tipo_usuario":context["tipo_usuario"],"municipio":context["municipio"], "ccaa":context["ccaa"], "conocer_felgtbi":context["conocer_felgtbi"], 
                                    "vih_usuario":context["vih_usuario"],"vih_diagnostico":context["vih_diagnostico"], "vih_tratamiento":context["vih_tratamiento"], 
                                    "us_edad":context["us_edad"], "us_pais_origen":context["us_pais_origen"], "us_genero":context["us_genero"], 
                                    "us_orientacion": context["us_orientacion"], "us_situacion_afectiva":context["us_situacion_afectiva"],
                                    "us_hablado":context["us_hablado"], "pro_ambito":context["pro_ambito"], "pro_especialidad": context["pro_especialidad"],
                                    "pro_vih_profesional":context["pro_vih_profesional"], "contenido":interaction["contenido"],
                                 "categoria_user_message": interaction["categoria_user_message"]})
    
    response = llm.invoke(prompt_value)

    #Guardamos la información en la tabla de interacciones
    db_insert_values_decisor(id_sesion=id_sesion,tipo_usuario="sistema",contenido=response.content,tipo_prompt="resolutor")  

def model_arbol(dict_preg_resp, input):
    '''
    Función auxiliar para la interacción del chat con el usuario
    '''
    cohere_api_key = os.getenv("COHERE_TRIAL_API_KEY") #API key

    dict_preg_resp = {
        pregunta: [respuesta.lower() for respuesta in respuestas]
        for pregunta, respuestas in dict_preg_resp.items()
    }

    examples = []

    response_schemas = [
        ResponseSchema(name="pendiente", description= "Booleano: Será el valor 'True' o 'False' en función de las explicaciones que te proporcionamos a continuación"),
        ResponseSchema(name="categoria_respuesta", description="Será vacío si no has podido categorizar la respuesta, y si no, será la categoria que corresponda segun te explicamos a continuacion"),
        ResponseSchema(name="message", description='''El texto que deberás darle al usuario según te explicamos a continuación''')]
    #Esquema/esqueleto de la respuesta del llm

    #Definimos lo que necesitamos para que la respuesta del llm tenga el formato de diccionario que le hemos indicado
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas) 
    format_instructions = output_parser.get_format_instructions()

    #Definimos la plantilla del prompt
    example_prompt = PromptTemplate(
        input_variables=["input", "dict_preg_resp"],
        template= '''  Input: {input}
                        Diccionario: {dict_preg_resp}
                    ''',
        partial_variables={"format_instructions": format_instructions}
    )

    #Le mostramos al llm los ejemplos creados antes
    few_shot_prompt = FewShotPromptTemplate(
        examples=examples,
        example_prompt=example_prompt,
        prefix='''Eres un chatbot experto en temas de vih, diseñado para guiar al usuario en un diálogo basado en preguntas y respuestas predeterminadas.

    Recibirás:
    1. Un "input": el mensaje del usuario.
    2. Un "dict_preg_resp": un diccionario con preguntas y, para cada una de ellas, sus posibles respuestas: {dict_preg_resp}. 

    Tu tarea es:
    - Identificar si el "input" que recibes coincide con una de las respuestas de la primera pregunta del diccionario.
    - Producir una salida en formato JSON con las siguientes claves:
        - "pendiente": 
            - `true` si hay más preguntas en el diccionario que tengan sentido que preguntemos. Por ejemplo, si 
            una usuaria dice que no es fértil, no le preguntes si está embarazada
            - `false` si no quedan más preguntas en el diccionario, bien porque se hayan acabado o bien porque las que queden
            no tenga sentido preguntarlas
        - "categoria_respuesta":
            - El valor del diccionario para esa pregunta que más se parezca al 'input' del usuario
            - Vacío si no hay coincidencias.
        - "message":
            - Si el "input" coincide o se aproxima a una de las posibles respuestas de esa pregunta:
                - 'message' será la siguiente pregunta disponible o "Gracias" si no hay más preguntas.
            - Si no coincide ni se aproxima, repite la misma pregunta.

    Notas importantes:
    - Siempre que te refieras al vih, utiliza minúsculas.
    - No brindas información técnica ni abordas temas fuera del vih.''',
        suffix="{input}\nOutput:",
        input_variables=["input", "dict_preg_resp"]
    )

    #Configuramos el modelo
    chat_model = ChatCohere(cohere_api_key=cohere_api_key, temperature=0, model="command-r-plus")
    user_input = input.lower()
    #Generamos el prompt
    final_prompt = few_shot_prompt.format(input=user_input, dict_preg_resp=dict_preg_resp)

    #Generamos la respuesta que nos devolverá el llm
    respuesta = chat_model.invoke(final_prompt)
    parsed_output = output_parser.parse(respuesta.content)
    return parsed_output

def model_arbol_interaction(id_sesion, dict_preg_resp, user_input):
    '''
    Función que, a partir de un listado de preguntas-respuestas del administrador (previamente filtrado)
    y la respuesta que da el usuario en el chat, permite interaccionar con el usuario de modo
    que éste responda todas las preguntas de los administradores y, finalmente, devuelve el recurso
    solicitado por el usuario en el chat
    '''
    if len(dict_preg_resp) > 1:
        resp = model_arbol(dict_preg_resp, user_input)
        del(dict_preg_resp[next(iter(dict_preg_resp))])
        
        #Guardamos la información en la tabla de interacciones
        db_insert_values_decisor(id_sesion=id_sesion,tipo_usuario= db_user_interaction(id_sesion)["tipo_usuario"],contenido=resp, tipo_prompt="resolutor")       

    else:
        print("Acabamos")
        #Almacenar en la SQL
        #return RECURSO
