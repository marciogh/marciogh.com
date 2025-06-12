import boto3
import json
from openai import OpenAI
from datetime import datetime
from collections import defaultdict

sm = boto3.client('secretsmanager', region_name='ap-southeast-2')
r = sm.get_secret_value(SecretId='OPENAI_API_KEY')
client = OpenAI(
   api_key=json.loads(
      (r['SecretString'])
   )['OPENAI_API_KEY']
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

   response = client.responses.create(
      model="gpt-4.1",
      input=query_params['q']
   )
   return {
      'statusCode': 200,
      'body': json.dumps(response.output_text),
      'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',         
            'Content-Type': 'application/json'
      }
   }

if __name__ == "__main__":
   print("main")