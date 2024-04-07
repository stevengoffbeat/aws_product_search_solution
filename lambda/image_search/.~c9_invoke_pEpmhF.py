import json
from typing import List
from opensearch_search import get_opensearch_client
from embeddings import get_image_embedding_sagemaker

response = {
    "statusCode": 200,
    "headers": {
        "Access-Control-Allow-Origin": '*'
    },
    "isBase64Encoded": False
}

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
    
    url = ""
    if "url" in evt_body.keys():
        url = evt_body['url'].strip()
    print('url:',url)
    
    index = ""
    if "index" in evt_body.keys():
        index = evt_body['index']
    print('index:',index)
    
    task = 'image-search'
    if "task" in evt_body.keys():
        task = evt_body['task']
    print('task:',task)
        
    embeddingType = 'sagemaker'
    if "embeddingType" in evt_body.keys():
        embeddingType = evt_body['embeddingType']
    
    embeddingEndpoint = ""
    if "embeddingEndpoint" in evt_body.keys():
        embeddingEndpoint = evt_body['embeddingEndpoint']
    
    topK = 3
    if "topK" in evt_body.keys():
        topK = int(evt_body['topK'])
    print('topK:',topK)

    vectorScoreThresholds = 0
    if "vectorScoreThresholds" in evt_body.keys() and evt_body['vectorScoreThresholds'] is not None:
        vectorScoreThresholds = float(evt_body['vectorScoreThresholds'])
    print('vectorScoreThresholds:', vectorScoreThresholds)

    classifyScoreThresholds = 0
    if "classifyScoreThresholds" in evt_body.keys() and evt_body['classifyScoreThresholds'] is not None:
        classifyScoreThresholds = float(evt_body['classifyScoreThresholds'])
    print('classifyScoreThresholds:', classifyScoreThresholds)

    vectorField = "image_vector_field"
    if "vectorField" in evt_body.keys():
        vectorField = evt_body['vectorField']
    print('vectorField:', vectorField)
    
    language = "chinese"
    if "language" in evt_body.keys():
        language = evt_body['language']
    print('language:', language)
    
    protentialTags = ""
    if "protentialTags" in evt_body.keys():
        protentialTags = evt_body['protentialTags']
    print('protentialTags:',protentialTags)
    
    products = []
    if task == 'image-search' and len(url) > 0:
        image_embedding = get_image_embedding_sagemaker(embeddingEndpoint,url)
        results = vector_search(index,image_embedding,vector_field=vectorField)
        for result in results:
            score = float(result['_score'])
            metadata = result['_source']['metadata']
            if score >= vectorScoreThresholds:
                products.append({'score':score,'source':metadata})
    
    elif task == 'classification':
        protentialTags = protentialTags.split(',')
        tag_confidentials = {}
        if len(embeddingEndpoint) >0 and len(url) > 0 and len(protentialTags) > 0:
            prompts = [f"the product is {item}" for item in protential_tags]
            base64_string = encode_image(url)
            inputs = {"image": base64_string, "prompt": prompts}
            
            output = run_inference(endpoint_name, inputs)
            print('output:',output)
            
            confidential_scores = json.loads(output)[0]
            print('confidential_scores:',confidential_scores)
            
            tag_confidentials = dict(zip(protential_tags,confidential_scores))
            print('tag_confidentials',tag_confidentials)
        
        response['body'] = json.dumps(
        {
            'tag_confidentials': tag_confidentials
        })
    
    if searchType == 'text' and len(index) > 0 and len(query) > 0:
        results = text_search(index,query,size=topK)
        for result in results:
            score = float(result['_score'])
            metadata = result['_source']['metadata']
            if score >= textScoreThresholds:
                products.append({'score':score,'source':metadata})
       
    elif searchType == 'vector' and embeddingType == 'sagemaker' and len(index) > 0 and len(query) > 0 and len(embeddingEndpoint) > 0:
        embedding = get_embedding_sagemaker(embeddingEndpoint,query,language=language)
        results = vector_search(index,embedding,vector_field=vectorField,size=topK)
        for result in results:
            score = result['_score']
            metadata = result['_source']['metadata']
            if score >= vectorScoreThresholds:
                products.append({'score':score,'source':metadata})
                
    response['body'] = json.dumps(
    {
        'products': products
    })      
    
    return response

        