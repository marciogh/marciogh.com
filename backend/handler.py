import boto3
import json
import os
from datetime import datetime
from collections import defaultdict
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders.s3_file import S3FileLoader
from langchain_community.document_loaders.text import TextLoader
from langchain.chains import RetrievalQA
import numpy as np

np.seterr(divide = 'ignore', over='ignore', invalid='ignore')
sm = boto3.client('secretsmanager', region_name='ap-southeast-2')
r = sm.get_secret_value(SecretId='OPENAI_API_KEY')
os.environ["OPENAI_API_KEY"] = json.loads((r['SecretString']))['OPENAI_API_KEY']
#loader = S3FileLoader(bucket="lambda-marciogh", key="data/data.txt")
loader = TextLoader("data/data.txt")
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

   query_params = event['queryStringParameters']

   context = """
   Answer summarized and factual questions as you are Marcio Ghiraldelli.
   You are being interviewed for an IT job.
   Here is the question:
   """
   query = context + query_params['q'];
   response = qa_chain.invoke({"query": query})

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
   print(lambda_handler({"queryStringParameters": {"q": "Which tech stacks you are more confortably with?"}}, {})['body'])
   print("\n")
   print(lambda_handler({"queryStringParameters": {"q": "Do you love your job?"}}, {})['body'])
   print("\n")
   print(lambda_handler({"queryStringParameters": {"q": "What's the ideal position for you"}}, {})['body'])
   print("\n")
   print(lambda_handler({"queryStringParameters": {"q": "What can you bring to our company"}}, {})['body'])
   print("\n")
   print(lambda_handler({"queryStringParameters": {"q": "What's your phone number?"}}, {})['body'])
   print("\n")
   print(lambda_handler({"queryStringParameters": {"q": "Do you feel anger?"}}, {})['body'])
   print("\n")
   print(lambda_handler({"queryStringParameters": {"q": "Have you ever killed anyone"}}, {})['body'])
   print("\n")
