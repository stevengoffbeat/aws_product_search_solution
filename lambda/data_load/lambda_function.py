import re
import os
import json
import traceback
import urllib.parse
import boto3
from datetime import datetime
import time
from opensearch_search import add_products,get_opensearch_client
from embeddings import get_image_embedding_sagemaker
import csv

s3_cli = boto3.client('s3')
bucketName = os.environ.get('bucket_name')

def lambda_handler(event, context):
    
    print("event:",event)
    evt_body = event['queryStringParameters']
    
    print("bucketName:",bucketName)
    
    index = ""
    if "index" in evt_body.keys():
        index = evt_body['index']
    print('index:',index)
    
    embeddingEndpoint = ""
    if "embeddingEndpoint" in evt_body.keys():
        embeddingEndpoint = evt_body['embeddingEndpoint']
        
    fileName = ""
    if "fileName" in evt_body.keys():
        fileName = evt_body['fileName']
    print("fileName:",fileName)
    
    task = "data_load"
    if "task" in evt_body.keys():
        task = evt_body['task']
    print("task:",task)
        
    imageColoumName = ''
    if "imageColoumName" in evt_body.keys():
        imageColoumName = evt_body['imageColoumName']
    print("imageColoumName:",imageColoumName)
        
    if task == 'data_load' and len(fileName) > 0 and len(embeddingEndpoint) > 0:
    
        now1 = datetime.now()#begin time
        localFile = "{}/{}".format('/tmp', fileName.split("/")[-1])
        s3_cli.download_file(Bucket=bucketName,
                             Key=fileName,
                             Filename=localFile
                             )
        print("finish download file:",fileName)
        
        product_info_list = []
        product_embedding_list = []
        image_embedding_list = []
        metadatas = []
        error_records = []
        i = 0
        
        
        csvfile=open(localFile,mode='r',encoding='utf-8')
        reader = [each for each in csv.DictReader(csvfile, delimiter=',')]
        
        
        for line in reader:
            print('line:',line)
            metadata = {}
            image_url = ''
            for key in line.keys():
                key_name = key.replace('\ufeff','').strip()
                if len(key_name) > 0:
                    metadata[key_name] = line[key].strip()
                    if len(imageColoumName) > 0 and key == imageColoumName:
                        image_url = line[key].strip()

            image_embedding = ''
            if len(image_url) > 0:
                print('in the len(image_url) > 0')
                try:
                    image_embedding = get_image_embedding_sagemaker(embeddingEndpoint,image_url)
                except:
                    error_records.append(metadata)
                    print("image embedding error at:" + str(i))
            else:
                continue
            
            if len(image_embedding) > 0:
                print('in the len(image_embedding) > 0')
                image_embedding_list.append(image_embedding)
                metadatas.append(metadata)
                product_info_list.append(image_url)
                
            i += 1
            print('i:',i)
            if i % 100 == 0:
                print('data number:',i)
            if i % 100 == 0 and len(image_embedding_list) > 0:
                add_products(index,product_info_list,product_embedding_list,metadatas,image_embedding_list)
                product_info_list = []
                product_embedding_list = []
                image_embedding_list = []
                metadatas = []
                now2 = datetime.now()
                print("File import takes time:",now2-now1)
                    
        print('total data number:',i)
        if len(image_embedding_list) > 0:
            add_products(index,product_info_list,product_embedding_list,metadatas,image_embedding_list)
        
        print('finish add products to opensearch,index is:' + index)
        now2 = datetime.now()
        print("Total File import takes time:",now2-now1)
        
        response = {
            "statusCode": 200,
            "headers": {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET'
            },
            "isBase64Encoded": False
        }
        response['body'] = json.dumps(
            {
                'result':"finish load the file:" + fileName,
                'records':i,
                'error_records':error_records
            }
        )
    elif task == 'opensearch_index':
        index_list = []
        try:
            #get indices list from opensearch
            client = get_opensearch_client()
    
            result = list(client.indices.get_alias().keys())
            
            for indice in result:
                if not indice.startswith("."):
                    index_list.append(indice)
            #         index_list.append({"name": indice, "s3_prefix": "", "aos_indice": indice})
            print(index_list)
            response = {
                "statusCode": 200,
                "headers": {
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,GET'
                },
                "isBase64Encoded": False
            }
            
            response['body'] = json.dumps(index_list)
            
        except Exception as e:
            print(e)
            response = {
                'statusCode': 500,
                'body': json.dumps('Internal Server Error')
            }
    elif task == 'sagemaker_endpoint':
        sagemaker = boto3.client('sagemaker')
        endpoints = sagemaker.list_endpoints()
        # 从响应中提取处于"InService"状态的所有端点的名称
        endpoint_names = [
            endpoint['EndpointName'] for endpoint in endpoints['Endpoints']
            if endpoint['EndpointStatus'] == 'InService'
        ]
        response = {
            "statusCode": 200,
            "headers": {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET'
            },
            "isBase64Encoded": False
        }
        response['body'] = json.dumps(endpoint_names)
        
    else:
    
        response = {
                'statusCode': 500,
                'body': json.dumps('Paremeters Server Error')
        }
        
    return response