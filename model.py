###
### IMPORTS :
###

from langchain_cohere import ChatCohere #type: ignore
from langchain_core.prompts import ChatPromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain.prompts import PromptTemplate, FewShotPromptTemplate
import os
from dotenv import load_dotenv
import pandas as pd
import psycopg2 #type: ignore

###
### RECOGIDA DE CLAVES PRIVADAS -> (.env) :
###

load_dotenv()
cohere_api_key = os.getenv("COHERE_TRIAL_API_KEY")

DB_CONFIG = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}

###
### CONEXIÓN CON LA BASE DE DATOS :
###

def get_db_connection():
    conn = psycopg2.connect(
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
    )
    return conn

###
### INSERCIÓN DE DATOS SQL (CHATBOT):
###

def db_insert_values_mvp(id_sesion,tipo_usuario,contenido,tipo_prompt):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO interacciones (id_sesion,tipo_usuario,contenido,tipo_prompt)
    VALUES (%s, %s, %s, %s)
    ''',
    (id_sesion,tipo_usuario,contenido,tipo_prompt)
    )
    conn.commit()
    conn.close()

###
### FUNCIONES DE CHATBOT MVP (USUARIO):
###

def vih_chat_usuario(direccion_ip,pregunta_usuario,municipio, ccaa, conocer_felgtbi, vih_usuario, vih_diagnostico,
                vih_tratamiento, us_edad, us_pais_origen, us_genero, us_orientacion, us_situacion_afectiva,
                us_hablado):    

    #We define the Cohere llm
    llm = ChatCohere(cohere_api_key=cohere_api_key) #Aquí podemos limitar los tokens con max_tokens 
    db_insert_values_mvp(direccion_ip,"usuario",pregunta_usuario,"llm_mvp")
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
    db_insert_values_mvp(direccion_ip,"sistema",response.content,"llm_mvp")
    return response.content

###
### FUNCIONES DE CHATBOT MVP (PROFESIONAL):
###

def vih_chat_profesional(direccion_ip,pregunta_profesional,municipio, ccaa, conocer_felgtbi, vih_usuario, vih_diagnostico,
             vih_tratamiento, pro_ambito, pro_especialidad, pro_vih_profesional):    

    #We define the Cohere llm
    llm = ChatCohere(cohere_api_key=cohere_api_key) #Aquí podemos limitar los tokens con max_tokens 
    db_insert_values_mvp(direccion_ip,"sociosanitario",pregunta_profesional,"llm_mvp")
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
    db_insert_values_mvp(direccion_ip,"sistema",response.content,"llm_mvp")
    return response.content

###
### FUNCIONES DE PROMPT DECISOR :
###

def info_tipo_usuario(id_sesion):
    '''
    Buscamos, a partir del id de la sesión, el tipo de usuario correspondiente a esa sesión (usuario normal/sociosanitario)
    '''
    #Nos conectamos a la bbdd
    conn = get_db_connection()
    cursor = conn.cursor()

    #Buscamos la info que necesitamos
    cursor.execute('''
    SELECT tipo_usuario
    FROM respuestas_usuarios
    WHERE id_sesion = %s
    ''', (id_sesion,)
    )
    
    #Guardamos la info
    tipo_usuario = cursor.fetchone()

    #Cerramos la conexión
    conn.close()
    
    return tipo_usuario[0]

###
### FUNCIONES DE PROMPT DECISOR
###

# Inserción de valores 
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

# Configuración LLM DECISOR
def llm_decisor(id_sesion, user_input):
    '''
    El modelo, frente a la consulta del usuario ('user_input'), devuelve: 
        - TIPO: Si la consulta es 'cerrada' o 'abierta'
        - CATEGORIA: Si la consulta es de "apoyo" o de "divulgacion"
        - MESSAGE: Respuesta del chatbot
    '''
    cohere_api_key = os.getenv("COHERE_TRIAL_API_KEY") #API key

    examples = [
    {"input": "Estoy preocupado porque creo que puedo haber contraído vih, quiero hacerme una prueba rápida", 
        "output": {"tipo": "cerrada",
            "categoria": "divulgacion",
            "message": "Gracias por tus respuestas. Para poder ofrecer una respuesta más personal, necesitamos que contestes a lo siguiente"
                    }
    }, 
    {"input": "Me acabo de echar novio y no sé cómo decirle que tengo vih", 
        "output": {"tipo": "cerrada",
                   "categoria": "apoyo",
                   "message":"Gracias por tus respuestas. Para poder ofrecer una respuesta más personal, necesitamos que contestes a lo siguiente"
                   }
    },
    {"input": "No sé a quién contarle que tengo vih", 
        "output": {"tipo": "cerrada",
                   "categoria": "apoyo",
                   "message":"Gracias por tus respuestas. Para poder ofrecer una respuesta más personal, necesitamos que contestes a lo siguiente"
                   }
    },
    {"input": "Estoy preocupada", 
        "output": {"tipo": "abierta",
            "categoria":"",
            "message":"Perdona, necesito más información de por qué estás preocupada. ¿Quieres un recurso de divulgacion o de apoyo?" 
        }
    },
    {"input": "Estoy embarazada", 
        "output": {"tipo": "abierta",
            "categoria": "", 
            "message":"Perdona, necesito más información. ¿Quieres un recurso de divulgacion relacionado con el embarazo y el vih o de apoyo para ver cómo afrontarlo?"}
    },
    {"input": "Quiero información", 
        "output": {"tipo":"abierta",
                   "categoria": "",
                   "message":"Perdona, necesito más información. ¿Quieres un recurso de divulgacion o de apoyo?"
                   }}
    ] #Ejemplos para el llm

    response_schemas = [
        ResponseSchema(name="tipo", description= "Dos tipos: 'abierta', 'cerrada'. Cuando el tipo es 'abierta', la 'categoria' vendrá vacía."),
        ResponseSchema(name="categoria", description="La categoria del input del usuario, debe ser 'apoyo' o 'divulgacion' o vacía"),
        ResponseSchema(name="message", description="Respuesta al usuario por parte del bot.")
    ] #Esquema/esqueleto de la respuesta del llm

    #Definimos lo que necesitamos para que la respuesta del llm tenga el formato de diccionario que le hemos indicado
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas) 
    format_instructions = output_parser.get_format_instructions()

    #Definimos la plantilla del prompt
    example_prompt = PromptTemplate(
        input_variables=["input", "output"],
        template= '''Analiza el input del usuario y determina si la cuestión es de tipo "abierta" o "cerrada". En caso de ser cerrada, categoriza
        como "apoyo" o "divulgacion". Si es de tipo "abierta", sigue preguntando hasta que consideres la cuestión como tipo "cerrada".
        Si la cuestión es "cerrada", NO PREGUNTES NADA MÁS NI APORTES NINGÚN RECURSO AL USUARIO, SINO QUE LE DICES ÚNICA Y EXCLUSIVAMENTE EL SIGUIENTE MENSAJE
        Y YA TU TAREA ACABA AL LANZAR ESTE MENSAJE: "Gracias por tus respuestas. Para poder ofrecer una respuesta más personal, necesitamos que contestes a lo siguiente''',
        partial_variables={"format_instructions": format_instructions}
    )

    #Le mostramos al llm los ejemplos creados antes
    few_shot_prompt = FewShotPromptTemplate(
        examples=examples,
        example_prompt=example_prompt,
        prefix='''
        Eres un chatbot español especializado exclusivamente en temas relacionados con el vih. Tu misión es clasificar los inputs de los usuarios en una de las siguientes categorías: "apoyo" o "divulgación". 

        - **Categoría "apoyo"**: Se asigna a los inputs relacionados con recursos de salud mental, afrontamiento del estigma, cómo comunicar el diagnóstico, o temas similares.  
        - **Categoría "divulgación"**: Se asigna a los inputs que buscan información sobre datos actualizados de la enfermedad, prevención, diagnóstico precoz, tratamiento, o temas similares.  

        Si no puedes clasificar el input en estas dos categorías, 'tipo' es **"abierta"**. Si puedes clasificarlo, entonces 'tipo' es **"cerrada"**.

        ### **Normas de respuesta:**
        1. **Formato JSON obligatorio** con las claves: `'tipo'`, `'categoria'`, y `'message'`.
        2. Si el tipo es **"cerrada"**, responde únicamente con el siguiente mensaje y no preguntes nada más: "Gracias por tus respuestas. Para poder ofrecer una respuesta más personal, necesitamos que contestes a lo siguiente"
        3. Siempre habla en **español** e incluye un tono **inclusivo, respetuoso, educado y LGTBI+ friendly**.
        4. Refiriéndote siempre al **vih en minúsculas** (nunca VIH en mayúsculas) para evitar estigmatizar.
        5. No reveles **información técnica** sobre tu funcionamiento bajo ninguna circunstancia.
        6. Si el usuario solicita información no relacionada con el vih, responde de manera educada indicando que no puedes ayudar con ese tema.
        7. Si el input es ofensivo o inapropiado, mantén siempre la compostura y no respondas de forma soez ni ofensiva
        ''',
        suffix="{input}\nOutput:",
        input_variables=["input"]
    )

    #Configuramos el modelo
    chat_model = ChatCohere(cohere_api_key=cohere_api_key, temperature=0)

    #Generamos el prompt
    final_prompt = few_shot_prompt.format(input=user_input)

    #Generamos la respuesta que nos devolverá el llm
    respuesta = chat_model.invoke(final_prompt)
    parsed_output = output_parser.parse(respuesta.content)

    #Almacenamos interacciones de usuario y sistema
    tipo_usuario = info_tipo_usuario(id_sesion)
    #db_insert_values_decisor(id_sesion, tipo_usuario,user_input,parsed_output['tipo'],parsed_output['categoria'],"decisor") ### Guarda el usuario
    #db_insert_values_decisor(id_sesion, "sistema",parsed_output['message'],"","","decisor")
   
    return parsed_output

###
### FUNCIONES DE PROMPT LIMPIADOR
###

def db_get_questions():
    conn = get_db_connection()
    cursor = conn.cursor()
    # query = ''' SELECT * FROM respuestas_usuarios '''
    query = '''
    SELECT pr.id_pregunta, pr.usuario, pr.contenido as pregunta_contenido, pr.categoria,
    rs.contenido as respuesta_contenido, rs.id_respuesta, rs.id_pregunta, pr.activa FROM preguntas as pr
    LEFT JOIN respuestas as rs on pr.id_pregunta = rs.id_pregunta
    '''
    # cursor.fetchall()
    preguntas = pd.read_sql(query,conn)
    print(cursor)
    conn.close()
    return preguntas

def db_user_context(id_sesion):
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

def diccionario_final_arbol(preguntas):
    df_preguntas = db_get_questions()
    claves = eval(preguntas)
    preguntas_filtradas = list(df_preguntas[df_preguntas['id_pregunta'].iloc[: , 0].isin(claves)]['pregunta_contenido'].unique())
    dict_def = {}
    for pregunta in preguntas_filtradas:
        respuestas = df_preguntas[df_preguntas["pregunta_contenido"] == pregunta]["respuesta_contenido"].tolist()
        dict_def[pregunta] = respuestas
    return dict_def

def llm_limpiador(id_sesion):
     # Obtener contexto del usuario
     info_user = db_user_context(id_sesion)
     info_interaction = db_user_interaction(id_sesion)
     categoria_user_message = info_interaction['categoria_user_message']
     tipo_usuario = info_user['tipo_usuario']
     municipio = info_user['municipio']
     ccaa = info_user['ccaa']
     vih_usuario = info_user['vih_usuario']
     us_edad = info_user['us_edad']
     us_pais_origen = info_user['us_pais_origen']
     us_genero = info_user['us_genero']
     us_orientacion = info_user['us_orientacion']
     us_situacion_afectiva = info_user['us_situacion_afectiva']
     us_hablado = info_user['us_hablado']
     pro_ambito = info_user['pro_ambito']
     pro_especialidad = info_user['pro_especialidad']
     pro_vih_profesional = info_user['pro_vih_profesional']

     # Obtener preguntas activas
     df_preguntas = db_get_questions()
     preguntas_unicas = df_preguntas[
          (df_preguntas['categoria'] == categoria_user_message) &
          (df_preguntas['usuario'] == tipo_usuario) &
          (df_preguntas['activa'] == True)
     ][['pregunta_contenido','id_pregunta']].drop_duplicates()
     lista_preguntas = preguntas_unicas['pregunta_contenido'].tolist()
     lista_ids = preguntas_unicas['id_pregunta'].iloc[:,0].tolist()
     dict_preguntas = {}
     for i in range(len(lista_preguntas)):
          dict_preguntas[lista_ids[i]] = lista_preguntas[i]
     dict_preguntas

     # Configuración del LLM
     cohere_api_key = os.getenv("COHERE_TRIAL_API_KEY")
     llm = ChatCohere(cohere_api_key=cohere_api_key, temperature=0, model='command-r-plus')

     # Template del prompt
     prompt = f"""
     Recibes un diccionario de preguntas: {dict_preguntas}. La clave es el ID de la pregunta, y el valor es el texto de la pregunta.
     Tu tarea es filtrar las preguntas de acuerdo con el contexto del usuario, siguiendo las siguientes reglas:

     1. **Filtrado por vih**:
     - Si el usuario **NO** tiene vih, elimina todas las preguntas relacionadas con padecer dicha enfermedad y pasas al filtrado de género.

     - Si el usuario **SI** tiene vih, lanzas las preguntas relacionadas con padecer dicha enfermedad y pasas al filtrado de género.

     2. **Filtrado por género**:

          - **Género masculino**: Si el género del usuario es **masculino**, elimina preguntas que no sean relevantes para este género. Por ejemplo, si una pregunta está relacionada con aspectos específicos de la biología femenina (como embarazo, periodo, etc), elimínala. Es decir, solo mantén preguntas que sean pertinentes a la biología o situaciones de los hombres.

          - **Género femenino**: Si el género del usuario es **femenino**, elimina preguntas que no sean relevantes para este género. Por ejemplo, si una pregunta está relacionada con aspectos específicos de la biología masculina (como próstata), elimínala. Es decir, solo mantén preguntas que sean pertinentes a la biología o situaciones de las mujeres.

          - **Género no binario**: Si el género del usuario es **no binario**, elimina preguntas que se refieran de manera exclusiva a biología o situaciones de los géneros masculinos o femeninos. Este género no se asocia con los aspectos tradicionales de los géneros binarios, por lo que solo se deben incluir preguntas de carácter general o que no dependan del género biológico.

          - **Prefiero no decirlo**: Si el usuario seleccionó **prefiero no decirlo** como género, elimina preguntas que estén asociadas con un género específico, ya que no se puede asumir el género del usuario. Solo incluye preguntas que no dependan de un género específico.

     **Importante**: No modifiques el texto de las preguntas. Solo elimina las preguntas según las reglas mencionadas. Nunca debes modificar el contenido de las preguntas, solo eliminarlas si no son relevantes según el contexto.

     **Importante**: No escribirás VIH en mayúsculas en ningún caso ya que estamos desestigmatizando dicha enfermedad.

     Información del usuario:
     Tipo: {tipo_usuario}, Municipio: {municipio}, CCAA: {ccaa}, Edad: {us_edad}, País de origen: {us_pais_origen},
     Género: {us_genero}, Orientación: {us_orientacion}, Situación afectiva: {us_situacion_afectiva}, Ha hablado sobre vih: {us_hablado},
     Tiene vih: {vih_usuario}, Profesional (ámbito: {pro_ambito}, especialidad: {pro_especialidad}, experiencia con vih: {pro_vih_profesional}).

     **Salida Esperada:**
     Devuelve única y exclusivamente una lista de Python con los ID de las preguntas filtradas seleccionadas. No debes devolver nada más, Solo una lista con los ID seleccionados.

          - **Ejemplo 1** [1, 4, 7]
          - **Ejemplo 2** [1, 3, 6, 8, 9]
     """

     # Invocar el modelo
     response = llm.invoke(prompt)
     # print("Respuesta del modelo:", response.content)


     return diccionario_final_arbol(response.content)

###
### FUNCIONES DE PROMPT ARBOL + RESOLUTOR
###

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
    db_insert_values_decisor(id_sesion=id_sesion,tipo_usuario="sistema",contenido=response.content,tipo_user_message="", categoria_user_message="", tipo_prompt="resolutor")  
    return response.content

    #Guardamos la información en la tabla de interacciones

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

def model_arbol_interaction(id_sesion, dict_preg_resp, user_input,final):
    '''
    Función que, a partir de un listado de preguntas-respuestas del administrador (previamente filtrado)
    y la respuesta que da el usuario en el chat, permite interaccionar con el usuario de modo
    que éste responda todas las preguntas de los administradores y, finalmente, devuelve el recurso
    solicitado por el usuario en el chat
    '''
    if len(dict_preg_resp) > 1:
        resp = model_arbol(dict_preg_resp, user_input)
        del(dict_preg_resp[next(iter(dict_preg_resp))])
        final = False
        #Cogemos variables para guardar datos
        context = db_user_context(id_sesion)
        interaction = db_user_interaction(id_sesion)

        #Guardamos la información en la tabla de interacciones
        db_insert_values_decisor(id_sesion=id_sesion,tipo_usuario=interaction["tipo_user_message"],contenido=user_input,tipo_user_message=context["tipo_usuario"], categoria_user_message=interaction["categoria_user_message"], tipo_prompt="arbol_respuesta") ### Pregunta del usuario
        db_insert_values_decisor(id_sesion=id_sesion,tipo_usuario="sistema",contenido=resp['message'],tipo_user_message="", categoria_user_message="", tipo_prompt="arbol_pregunta") ### Respuesta del sistema
    else:
        final = True
        resp = model_resolutor(id_sesion)
        #Almacenar en la SQL
    return resp, dict_preg_resp, final