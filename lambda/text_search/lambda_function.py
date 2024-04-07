import json
from typing import List
from opensearch_search import get_opensearch_client
from embeddings import get_embedding_sagemaker

response = {
    "statusCode": 200,
    "headers": {
        "Access-Control-Allow-Origin": '*'
    },
    "isBase64Encoded": False
}

def text_search(index: str, search_term: str, size: int = 10):
    client = get_opensearch_client()
    offset = 0
    collapse_size = int(max(size / 15, 15))

    results = client.search(index = index, body={
                "from": offset,
                "size": size,
                "query": {
                    "dis_max" : {
                        "queries" : [
                            { "match_bool_prefix" : { "metadata.product_name" : { "query": search_term, "boost": 1.2 }}},
                            { "match_bool_prefix" : { "metadata.description_info" : { "query": search_term, "boost": 0.6 }}}
                        ],
                        "tie_breaker" : 0.7
                    }
                },
                "fields":[
                    "_id"
                ]
            }
        )

    return results['hits']['hits']

def vector_search(index: str, query_vector: List[float], size: int = 10,vector_field: str = "vector_field"):
    client = get_opensearch_client()
    offset = 0
    collapse_size = int(max(size / 15, 15))

    results = client.search(index = index, body={
                "size": size,
                "query": {"knn": {vector_field: {"vector": query_vector, "k": size}}},
            }
        )

    return results['hits']['hits']



def lambda_handler(event, context):
    
    print("event:",event)
    evt_body = event['queryStringParameters']
    
    query = ""
    if "query" in evt_body.keys():
        query = evt_body['query'].strip()
    print('query:',query)
    
    index = ""
    if "index" in evt_body.keys():
        index = evt_body['index']
    print('index:',index)
    
    searchType = 'text'
    if "searchType" in evt_body.keys():
        searchType = evt_body['searchType']
    print('searchType:',searchType)
        
    embeddingType = 'sagemaker'
    if "embeddingType" in evt_body.keys():
        embeddingType = evt_body['embeddingType']
    
    embeddingEndpoint = ""
    if "embeddingEndpoint" in evt_body.keys():
        embeddingEndpoint = evt_body['embeddingEndpoint']

    textSearchNumber = 0
    if "textSearchNumber" in evt_body.keys() and evt_body['textSearchNumber'] is not None:
        textSearchNumber = int(evt_body['textSearchNumber'])
    print('textSearchNumber:', textSearchNumber)
    
    vectorSearchNumber = 0
    if "vectorSearchNumber" in evt_body.keys() and evt_body['vectorSearchNumber'] is not None:
        vectorSearchNumber = int(evt_body['vectorSearchNumber'])
    print('vectorSearchNumber:', vectorSearchNumber)

    vectorScoreThresholds = 0
    if "vectorScoreThresholds" in evt_body.keys() and evt_body['vectorScoreThresholds'] is not None:
        vectorScoreThresholds = float(evt_body['vectorScoreThresholds'])
    print('vectorScoreThresholds:', vectorScoreThresholds)

    textScoreThresholds = 0
    if "textScoreThresholds" in evt_body.keys() and evt_body['textScoreThresholds'] is not None:
        textScoreThresholds = float(evt_body['textScoreThresholds'])
    print('textScoreThresholds:', textScoreThresholds)

    vectorField = "vector_field"
    if "vectorField" in evt_body.keys():
        vectorField = evt_body['vectorField']
    print('vectorField:', vectorField)
    
    language = "chinese"
    if "language" in evt_body.keys():
        language = evt_body['language']
    print('language:', language)
    
    productIdName = ""
    if "productIdName" in evt_body.keys():
        productIdName = evt_body['productIdName']
    print('productIdName:', productIdName)
    
    products = []
    product_id_set = set()
    if (searchType == 'text' or searchType == 'mix') and len(index) > 0 and len(query) > 0:
        results = text_search(index,query,size=textSearchNumber)
        for result in results:
            score = float(result['_score'])
            metadata = result['_source']['metadata']
            if score >= textScoreThresholds:
                if len(productIdName) > 0:
                    product_id = metadata[productIdName]
                    if product_id not in product_id_set:
                        products.append({'score':score,'source':metadata})
                        product_id_set.add(product_id)
                else:
                    products.append({'score':score,'source':metadata})
       
    if (searchType == 'vector' or searchType == 'mix') and embeddingType == 'sagemaker' and len(index) > 0 and len(query) > 0 and len(embeddingEndpoint) > 0:
        embedding = get_embedding_sagemaker(embeddingEndpoint,query,language=language)
        results = vector_search(index,embedding,size=vectorSearchNumber,vector_field=vectorField)
        for result in results:
            score = result['_score']
            metadata = result['_source']['metadata']
            if score >= vectorScoreThresholds:
                if len(productIdName) > 0:
                    product_id = metadata[productIdName]
                    if product_id not in product_id_set:
                        products.append({'score':score,'source':metadata})
                        product_id_set.add(product_id)
                else:
                    products.append({'score':score,'source':metadata})
    print('products:',products)
                
    response['body'] = json.dumps(
    {
        'products': products
    })      
    
    return response

        