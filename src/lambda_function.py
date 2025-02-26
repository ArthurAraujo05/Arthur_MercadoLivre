import json
import boto3
import uuid
from datetime import datetime
import os
import requests

URL_QUEUE = os.environ.get("URL_QUEUE")

def lambda_handler(event, context):
    URL_INFRAESTRUTURA = "https://2xnyepggle.execute-api.us-east-1.amazonaws.com/v1"
    client_sqs = boto3.client('sqs')

    dynamodb = boto3.resource('dynamodb')
    tabela = dynamodb.Table('arthur_pedido')

    body = json.loads(event["body"])
    produtos = body.get("produtos")
    url_transportadora = body.get("url_transportadora")

    for produto in produtos:
      response_get = requests.get(URL_INFRAESTRUTURA + "/" + str(produto['id_produto']))
      data = response_get.json()

      response = tabela.put_item(
         Item={
            "id_pedido": str(uuid.uuid4()),
            "id_produto": produto['id_produto'],
            "quantidade": produto['quantidade'],
            "url_transportadora": url_transportadora,
            "nome_produto": data['nome_produto'],
            "nome_loja": "Adidas",
            "data_pedido": str(datetime.now())
         }
         
      )

    messages = [
        {
            "Id": str(uuid.uuid4()),  
            "MessageBody": json.dumps({
                "produtos": produtos,
                "url_transportadora": url_transportadora
            })
        }
    ]

    msg = client_sqs.send_message_batch(
      QueueUrl = URL_QUEUE,
      Entries = messages
    ) 

    return {
      "statusCode": 200,
      "headers": {
        "Content-Type": "application/json"
      },
      "body": json.dumps({
                "produtos": produtos,
                "url_transportadora": url_transportadora
      })
    }