import json
import boto3  # biblioteca para manipular serviços da AWS
import uuid  # biblioteca para gerar UUIDs (identificadores únicos)
from datetime import datetime
import os
import requests

sqs = boto3.client('sqs')
dynamodb = boto3.resource('dynamodb')
tabela = dynamodb.Table('pedido_arthur')  # nome da tabela no DynamoDB que eu criei
URL_INFRAESTRUTURA = "https://aqjirlvgo4.execute-api.us-east-1.amazonaws.com/v1"

def lambda_handler(event, context):
    client_sqs = boto3.client('sqs')
    #body = json.loads(event["body"])
    produtos = event['produtos']
 
    url_transportadora = event['url_transportadora']

    for produto in produtos:
        response_get = requests.get(URL_INFRAESTRUTURA + "/" + str(produto['id_produto']))
        data = response_get.json()

        response = tabela.put_item(
            Item={
                "id": str(uuid.uuid4()),  # Gera um ID único obrigatório
                "id_pedido": str(uuid.uuid4()),
                "id_produto": produto['id_produto'],
                "quantidade": produto['quantidade'],
                "url_transportadora": url_transportadora,
                "nome_produto": data['nome_produto'],
                "nome_loja": "Mercado Livre",
                "data_pedido": str(datetime.now())
            }
        )

    message_body = json.dumps({'produtos': produtos,'url_transportadora': url_transportadora})  

    sqs.send_message(
        QueueUrl='https://sqs.us-east-1.amazonaws.com/199299155478/ArthurSQS',
        MessageBody=message_body
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

