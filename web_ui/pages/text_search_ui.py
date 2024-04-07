import requests
import streamlit as st
import streamlit.components.v1 as components
import json
from datetime import datetime
import pandas as pd

def product_search(query,
                invoke_url,
                endpoint_name: str = '',
                searchType: str = 'text',
                textSearchNumber: int = 3,
                vectorSearchNumber: int = 0,
                textScoreThresholds: float = 0,
                vectorScoreThresholds: float = 0,
                language: str = '',
                product_id_name: str = ''
                ):
    url = invoke_url + '/text_search?'
    url += ('&query='+query)
    url += ('&searchType='+searchType)
    if len(endpoint_name) > 0:
        url += ('&embeddingEndpoint='+endpoint_name)
    if textSearchNumber > 0:
        url += ('&textSearchNumber='+textSearchNumber)
    if vectorSearchNumber > 0:
        url += ('&vectorSearchNumber='+vectorSearchNumber)
    if textScoreThresholds > 0:
        url += ('&textScoreThresholds='+textScoreThresholds)
    if vectorScoreThresholds > 0:
        url += ('&vectorScoreThresholds='+vectorScoreThresholds)
    if len(language) > 0:
        url += ('&language='+language)
    if len(product_id_name) > 0:
        url += ('&product_id_name='+product_id_name)
    
    print('url:',url)
    response = requests.get(url)
    result = response.text
    result = json.loads(result)
    print("result:",result)
    products = result['products']

    return products



# Re-initialize the chat
def new_query() -> None:
    st.session_state.query = ''
    
with st.sidebar:

    search_invoke_url = st.text_input(
        "Please input a product search api url",
        "",
        key="product_search_invoke_url",
    )
    product_search_sagemaker_endpoint = st.text_input(
        "Please input product search sagemaker endpoint",
        "",
        key="product_search_endpoint",
    )
    
    search_type  = st.radio("Search Type",["text","vector",'mix'])
    st.write('For text search type:')
    textSearchNumber = st.slider("Search Number",min_value=1, max_value=10, value=3, step=1)
    textScoreThresholds = st.slider("Score Threshold",min_value=0, max_value=50, value=30, step=1)
    
    st.write('For vector search type:')
    vectorSearchNumber = st.slider("Search Number",min_value=1, max_value=10, value=3, step=1)
    vectorScoreThresholds = st.slider("Score Threshold",min_value=0, max_value=1, value=0.5, step=0.01)

# Add a button to start a new chat
st.sidebar.button("New Query", on_click=new_query, type='primary')

st.session_state.query = st.text_input(label="Please input query", value="")

if st.button('Product Search'):
    if len(st.session_state.query) ==0:
        st.write("Query is None")
    elif len(search_invoke_url) == 0:
        st.write("Search invoke url is None")
    elif len(product_search_sagemaker_endpoint) == 0:
        st.write("Embedding sagemaker endpoint is None")
        
    products = product_search(st.session_state.query,
                              search_invoke_url,
                              product_search_sagemaker_endpoint,
                              search_type,
                              textSearchNumber,
                              vectorSearchNumber,
                              textScoreThresholds,
                              vectorScoreThresholds
                             )
            
    items_num = len(products)
    if items_num == 0:
        response = '没找到符合要求的商品，请试试其它问题吧！'
        st.write(response)
    elif items_num >= 1:
        st.write('搜索结果：')
        col1, col2, col3 = st.columns(3)
        item_name_list = []
        image_list = []
        description_list = []
        scores_list = []
            
        for product in products:
            score = product['score']
            scores_list.append(score)
            source = product['source']
            media_url = source['media_url']
            product_name = source['product_name']
            description = source['description_info']
            item_name_list.append(product_name)
            image_list.append(media_url)
            description_list.append(description)
            
        with col1:
            if items_num >= 1:
                st.write('product_name:' + item_name_list[0])
                st.write('description_info:' + description_list[0])
                st.write('score:' + scores_list[0])
                st.image(image_list[0])
            if items_num >= 4:
                st.write('product_name:' +item_name_list[3])
                st.write('description_info:' + description_list[3])
                st.write('score:' + scores_list[3])
                st.image(image_list[3])
            if items_num >= 7:
                st.write('product_name:' +item_name_list[6])
                st.write('description_info:' + description_list[6])
                st.write('score:' + scores_list[6])
                st.image(image_list[6])
        with col2:
            if items_num >= 2:
                st.write('product_name:' +item_name_list[1])
                st.write('description_info:' + description_list[1])
                st.write('score:' + scores_list[1])
                st.image(image_list[1])
            if items_num >= 5:
                st.write('product_name:' +item_name_list[4])
                st.write('description_info:' + description_list[4])
                st.write('score:' + scores_list[4])
                st.image(image_list[4])
            if items_num >= 8:
                st.write('product_name:' +item_name_list[7])
                st.write('description_info:' + description_list[7])
                st.write('score:' + scores_list[7])
                st.image(image_list[7])
        with col3:
            if items_num >= 3:
                st.write('product_name:' +item_name_list[2])
                st.write('description_info:' + description_list[2])
                st.write('score:' + scores_list[2])
                st.image(image_list[2])
            if items_num >= 6:
                st.write('product_name:' +item_name_list[5])
                st.write('description_info:' + description_list[5])
                st.write('score:' + scores_list[5])
                st.image(image_list[5])
            if items_num >= 9:
                st.write('product_name:' +item_name_list[8])
                st.write('description_info:' + description_list[8])
                st.write('score:' + scores_list[8])
                st.image(image_list[8])