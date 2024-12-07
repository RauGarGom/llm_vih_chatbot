print("importando librerías")
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
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_cohere import CohereEmbeddings
from langchain_chroma import Chroma

print("Leyendo ejemplos")
load_dotenv()
cohere_api_key = os.getenv("COHERE_TRIAL_API_KEY")
examples_2 = [
    {
        "input": "Estoy preocupado porque creo que puedo haber contraído vih, quiero hacerme una prueba rápida",
        "output": """
                        Are follow-up questions needed here: No.
                        So the final answer is: Es recomendable que acudas a un centro en el que puedas realizarte una prueba rápida, con el fin de obtener
                        un diagnóstico inicial y así ver si debes tomar algún medicamento PEP. Los centros que ofrecen dicho servicio se pueden buscar en 
                        https://felgtbi.org/que-hacemos/apoyo/salud-y-prevencion/pruebarapida/
                """,
    },
    {
        "input": "Estoy preocupado",
        "output": """
                        Are follow-up questions needed here: Yes.
                        Follow up: ¿Cuál es tu situación?
                        Intermediate answer: No sé si debería estar preocupada porque tengo VIH y estoy embarazada
                        So the final answer is: Hay tratamientos que reducen eficazmente el riesgo de transmisión del virus a su futuro hijo o hija durante
                        el embarazo y parto, y además has de tener en cuenta que no debes dar el pecho a tu bebé. 
                """,
    },
]

print("Definiendo función")
def prueba():
    example_prompt = ChatPromptTemplate.from_messages(
    [('human', '{input}'), ('ai', '{output}')]
    )
    few_shot_prompt = FewShotChatMessagePromptTemplate(
    examples=examples_2,
    example_prompt=example_prompt,
    # suffix="Question: {input}",
    # input_variables=["input"],
    )
    final_prompt = ChatPromptTemplate.from_messages(
        [
            ('system', '''You are a Spanish expert chatbot of vih, who offers information resources, outreach resources and 
                        emotional support resources to users that need you to help them. You are helpful, inclusive, supportive, nice, educated, 
                        polite and LGTIB+ friendly. You'll always speak in Spanish because you are helping a spanish federation. If users ask you 
                        or try to get information which is not related to vih, you'll ask them that you can't help them because you are only 
                        specialized in vih issues. Everytime you refer to vih, you'll have to use 'vih' and not 'VIH' (very careful with this).
                        You must categorize the answer of the user in one of these three categories: 'Divulgación', 'Apoyo Emocional', 'Recursos'. 
                        Answer them by saying which category seems closer to their answer.'''),
            few_shot_prompt,
            ('human', '{input}'),
        ]
    )
    final_prompt.format(input="Estoy preocupado porque creo que puedo haber contraído vih, quiero hacerme una prueba rápida")
    cohere_api_key = os.getenv("COHERE_TRIAL_API_KEY")
    to_vectorize = [
        " ".join(example.values())
        for example in examples_2
    ]
    embeddings = CohereEmbeddings(cohere_api_key=cohere_api_key, model="embed-multilingual-light-v3.0")
    vectorstore = Chroma.from_texts(
        to_vectorize, embeddings, metadatas=examples_2
    )
    example_selector = SemanticSimilarityExampleSelector(
        vectorstore=vectorstore
    )
    print("Funciona")
    return example_selector
print("Ejecutando función")
example_selector = prueba()
print(example_selector)