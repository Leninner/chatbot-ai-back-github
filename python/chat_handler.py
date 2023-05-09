import os
import json
import openai
from utils.postgres_db_chat_message_history import PostgresChatMessageHistory
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.embeddings import OpenAIEmbeddings
from utils.supabase_vectorstore import SupabaseVectorStore
from supabase.client import Client, create_client
from langchain.chains import LLMChain
from typing import List, Tuple
from langchain.chains.combine_documents.base import (
    format_document,
)
from langchain.prompts.prompt import PromptTemplate

openai.api_key = os.environ["OPENAI_API_KEY"]
table_name = 'conversations-' + os.environ['ENVIRONMENT']
supabase_url = os.environ['SUPABASE_URL']
supabase_key = os.environ['SUPABASE_KEY']
connection_string=os.environ['POSTGRES_CONNECTION_STRING_SUPABASE']

def handler(event, context):    
  responseHeaders = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
  }
    
  request_body = event['body']
  request_data = json.loads(request_body)
  prompt = request_data['prompt']
  client_id = request_data['client_id'] if 'client_id' in request_data else None
  session_id = request_data['session_id'] if 'session_id' in request_data else None

  try:
    llm_chat = ChatOpenAI(temperature=0)
    chat_prompt = get_chat_prompt_template()
    context = get_context(supabase_url=supabase_url, supabase_key=supabase_key, client_id=client_id, prompt=prompt)
    history = PostgresChatMessageHistory(connection_string=connection_string, session_id=session_id)
    history.add_user_message(prompt)

    question_generator = LLMChain(llm=llm_chat, prompt=chat_prompt, verbose=True)
    chat_history = history.messages

    result = question_generator.predict(question=prompt, chat_history=chat_history, context=context)
    history.add_ai_message(result)

    message_response = {
      'session_id': history.session_id,
      'response': result,
    }

    return {
        'statusCode': 200,
        'body': json.dumps(message_response),
        'headers': responseHeaders
    }
  except Exception as e:
      print('error', e)
      return {
          'statusCode': 500,
          'body': json.dumps("No se pudo generar la respuesta para la pregunta " + prompt),
          'headers': responseHeaders
      }
  
def get_chat_prompt_template():
  system_template="""
  Lo que sigue es una conversación amistosa entre un humano y una IA. 
  La IA le gusta hablar y proporciona muchos detalles específicos del contexto delimitado por las triple comillas invertidas. 
  Si la IA no sabe la respuesta a una pregunta que no se encuentra en el contexto, dice sinceramente que no sabe.
  
  Contexto: ```{context}```
  """
    
  chat_prompt = ChatPromptTemplate.from_messages([
              SystemMessagePromptTemplate.from_template(system_template),
              MessagesPlaceholder(variable_name="chat_history"),
              HumanMessagePromptTemplate.from_template("{question}")
            ])

  return chat_prompt 

def get_context(supabase_url: str, supabase_key: str, client_id: str, prompt: str) -> SupabaseVectorStore:
    supabase: Client = create_client(supabase_url, supabase_key)

    embeddings = OpenAIEmbeddings()
    vector_store = SupabaseVectorStore(
        client=supabase,
        embedding=embeddings,
        table_name="documents",
        query_name="match_documents",
        client_id=client_id
    )

    docs = vector_store.as_retriever().get_relevant_documents(prompt)
    doc_strings = [format_document(doc, PromptTemplate(input_variables=["page_content"], template="{page_content}")) for doc in docs]
    context = "\n\n".join(doc_strings)
    return context
