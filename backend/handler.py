import boto3
import json
import os
from datetime import datetime
from collections import defaultdict
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.document_loaders.s3_file import S3FileLoader
from langchain.chains import RetrievalQA

sm = boto3.client('secretsmanager', region_name='ap-southeast-2')
r = sm.get_secret_value(SecretId='OPENAI_API_KEY')
os.environ["OPENAI_API_KEY"] = json.loads((r['SecretString']))['OPENAI_API_KEY']
loader = S3FileLoader(bucket="lambda-marciogh", key="data/data.txt")
documents = loader.load()
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(documents, embeddings)
retriever = vectorstore.as_retriever()
llm = ChatOpenAI(model="gpt-4.1")
qa_chain = RetrievalQA.from_chain_type(
   llm=llm,
   retriever=retriever,
   return_source_documents=True
)

ratelimiter = defaultdict(int)

def lambda_handler(event, context):

   # time slot ratelimiter
   now = datetime.now()
   ratelimiter[int(now.timestamp()/60)] += 1;
   if (ratelimiter[int(now.timestamp()/60)] >= 20):
      return {
         'statusCode': 429,
         'body': '429 too many requests',
         'headers': {
               'Access-Control-Allow-Headers': 'Content-Type',
               'Access-Control-Allow-Origin': '*',
               'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',         
               'Content-Type': 'application/json'
         }
      }

   method = event['httpMethod']
   path = event['path']
   headers = event['headers']
   query_params = event['queryStringParameters']
   body = event['body']

   print(f"Method: {method}, Path: {path}")
   print(f"Headers: {headers}, Params: {query_params}")
   print(f"Body: {body}")

   response = qa_chain.invoke({"query": query_params['q']})

   return {
      'statusCode': 200,
      'body': json.dumps(response['result']),
      'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',         
            'Content-Type': 'application/json'
      }
   }

if __name__ == "__main__":
   print("main")