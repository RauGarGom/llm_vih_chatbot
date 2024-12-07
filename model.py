import cohere  #LLLM used for the development of the application
from langchain_cohere import ChatCohere
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, Form
from langchain.prompts.few_shot import FewShotPromptTemplate #for creating prompts with few-shot examples
from langchain.prompts.prompt import PromptTemplate #for formatting the few-shot examples
from langchain.prompts import FewShotChatMessagePromptTemplate
from langchain.schema import HumanMessage, AIMessage, SystemMessage
load_dotenv()
cohere_api_key = os.getenv("COHERE_TRIAL_API_KEY")

def vih_chat_usuario(pregunta_usuario,municipio, ccaa, conocer_felgtbi, vih_usuario, vih_diagnostico,
             vih_tratamiento, us_edad, us_pais_origen, us_genero, us_orientacion, us_situacion_afectiva,
             us_hablado):    

    #We define the Cohere llm
    llm = ChatCohere(cohere_api_key=cohere_api_key) #Aquí podemos limitar los tokens con max_tokens 

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
    return response.content