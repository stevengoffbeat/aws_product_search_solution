import json
from typing import List
from opensearch_search import get_opensearch_client
from embeddings import get_image_embedding_sagemaker,encode_image,run_inference

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
    
    vectorSearchNumber = 3
    if "vectorSearchNumber" in evt_body.keys():
        vectorSearchNumber = int(evt_body['vectorSearchNumber'])
    print('vectorSearchNumber:',vectorSearchNumber)

    vectorScoreThresholds = 0
    if "vectorScoreThresholds" in evt_body.keys() and evt_body['vectorScoreThresholds'] is not None:
        vectorScoreThresholds = float(evt_body['vectorScoreThresholds'])
    print('vectorScoreThresholds:', vectorScoreThresholds)

    vectorField = "image_vector_field"
    if "vectorField" in evt_body.keys():
        vectorField = evt_body['vectorField']
    print('vectorField:', vectorField)
    
    protentialTags = ""
    if "protentialTags" in evt_body.keys():
        protentialTags = evt_body['protentialTags']
    print('protentialTags:',protentialTags)
    
    
    if task == 'image-search' and len(url) > 0 and len(embeddingEndpoint) >0:
        image_embedding = get_image_embedding_sagemaker(embeddingEndpoint,url)
        results = vector_search(index,image_embedding,size=vectorSearchNumber,vector_field=vectorField)
        products = []
        for result in results:
            score = float(result['_score'])
            metadata = result['_source']['metadata']
            if score >= vectorScoreThresholds:
                products.append({'score':score,'source':metadata})
        
        response['body'] = json.dumps(
            {
                'products': products
            }
        )  
    
    elif task == 'classification' and len(embeddingEndpoint) >0 and len(url) > 0 and len(protentialTags) > 0:
        protentialTags = protentialTags.split(',')
        tag_confidentials = {}
    
        prompts = [f"the product is {item}" for item in protentialTags]
        base64_string = encode_image(url)
        inputs = {"image": base64_string, "prompt": prompts}
        
        output = run_inference(embeddingEndpoint, inputs)
        confidentialScores = output[0]
        print('confidentialScores:',confidentialScores)
        
        tagConfidentials = dict(zip(protentialTags,confidentialScores))
        print('tagConfidentials',tagConfidentials)
        
        response['body'] = json.dumps(
            {
                'tagConfidentials': tagConfidentials
            }
        )
    else:
        response['body'] = json.dumps(
            {
                'error': "Parameters error!"
            }
        )
    
    return response