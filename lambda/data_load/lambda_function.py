import re
import os
import json
import traceback
import urllib.parse
import boto3
from datetime import datetime
import time
from opensearch_search import add_products,get_opensearch_client
from embeddings import get_image_embedding_sagemaker,get_embedding_sagemaker
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
    
    imageEmbeddingEndpoint = ""
    if "imageEmbeddingEndpoint" in evt_body.keys():
        imageEmbeddingEndpoint = evt_body['imageEmbeddingEndpoint']
        
    textEmbeddingEndpoint = ""
    if "textEmbeddingEndpoint" in evt_body.keys():
        textEmbeddingEndpoint = evt_body['textEmbeddingEndpoint']
        
    fileName = ""
    if "fileName" in evt_body.keys():
        fileName = evt_body['fileName']
    print("fileName:",fileName)
    
    task = "data_load"
    if "task" in evt_body.keys():
        task = evt_body['task']
    print("task:",task)

    loadType = "text"  # text / image / text_and_image
    if "loadType" in evt_body.keys():
        loadType = evt_body['loadType']
    print("loadType:",loadType)
        
    imageColoumName = ''
    if "imageColoumName" in evt_body.keys():
        imageColoumName = evt_body['imageColoumName']
    print("imageColoumName:",imageColoumName)
    
    language = 'english'
    if "language" in evt_body.keys():
        language = evt_body['language']
    print("language:",language)
    
    textColoumName = ''
    if "textColoumName" in evt_body.keys():
        textColoumName = evt_body['textColoumName']
    print("textColoumName:",textColoumName)
    textColoumNameList = textColoumName.split(',')
        
    if task == 'data_load' and len(fileName) > 0 and (len(textEmbeddingEndpoint) > 0 or len(imageEmbeddingEndpoint) > 0):
    
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
            product_info = ''
            for key in line.keys():
                key_name = key.replace('\ufeff','').strip()
                value = line[key].strip()
                if len(key_name) > 0:
                    metadata[key_name] = value
                    if len(imageColoumName) > 0 and key_name == imageColoumName:
                        image_url = value
                    if len(textColoumNameList) > 0 and key_name in textColoumNameList:
                        if len(product_info) == 0:
                            product_info = value
                        else:
                            product_info += (',' + value)

            image_embedding = ''
            if loadType.find('image') >= 0 and len(image_url) > 0 and len(imageEmbeddingEndpoint) > 0:
                try:
                    image_embedding = get_image_embedding_sagemaker(imageEmbeddingEndpoint,image_url)
                except:
                    error_records.append(metadata)
                    print("image embedding error at:" + str(i))
            
                if len(image_embedding) > 0:
                    image_embedding_list.append(image_embedding)
                    product_info_list.append(image_url)
            
            text_embedding = ''
            if loadType.find('text') >= 0 and len(product_info) > 0 and len(textEmbeddingEndpoint) > 0:
                try:
                    text_embedding = get_embedding_sagemaker(textEmbeddingEndpoint,product_info,language=language)
                except:
                    error_records.append(metadata)
                    print("text embedding error at:" + str(i))
                    
                if len(text_embedding) > 0:
                    product_embedding_list.append(text_embedding)
                    product_info_list.append(product_info)
                    
            if loadType.find('image') >= 0 and loadType.find('text') >= 0:
                if len(image_embedding) == 0 or len(text_embedding) == 0:
                    continue
            elif loadType.find('image') >= 0 and len(image_embedding) == 0:
                continue
            elif loadType.find('text') >= 0 and len(text_embedding) == 0:
                continue
                
            metadatas.append(metadata)
            i += 1
            # print('i:',i)
            # if i % 100 == 0:
            #     print('data number:',i)
            # if i % 100 == 0 and len(image_embedding_list) > 0:
            #     add_products(index,product_info_list,product_embedding_list,metadatas,image_embedding_list)
            #     product_info_list = []
            #     product_embedding_list = []
            #     image_embedding_list = []
            #     metadatas = []
            #     now2 = datetime.now()
            #     print("File import takes time:",now2-now1)
                    
        print('total data number:',i)
        if len(image_embedding_list) > 0 or len(product_embedding_list) > 0:
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
        }
        response['body'] = json.dumps(
            {
                'result':"Paremeters Server Error"
            }
        )
        
    return response