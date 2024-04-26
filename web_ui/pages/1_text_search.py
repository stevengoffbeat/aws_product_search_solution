import requests
import streamlit as st
import streamlit.components.v1 as components
import json
from datetime import datetime
import pandas as pd
import ast


def get_sagemaker_endpoint(invoke_url):
    url = invoke_url + '/text_search?'
    url += ('&task=sagemaker_endpoint')
    print('url:',url)
    response = requests.get(url)
    response = ast.literal_eval(response.text)
    print('sagemaker endpoint:',response)
    return response

def get_openserch_index(invoke_url):
    url = invoke_url + '/text_search?'
    url += ('&task=opensearch_index')
    print('url:',url)
    response = requests.get(url)
    response = ast.literal_eval(response.text)
    print('opensearch index:',response)
    return response

def product_search(query,
                invoke_url,
                index,
                endpoint_name: str = '',
                rerankerEndpoint: str = '',
                searchType: str = 'text',
                textSearchNumber: int = 3,
                vectorSearchNumber: int = 0,
                textScoreThresholds: float = 0,
                vectorScoreThresholds: float = 0,
                language: str = '',
                productIdName: str = '',
                description: str= '',
                keywords: str=''
                ):
    url = invoke_url + '/text_search?'
    url += ('&query='+query)
    url += ('&searchType='+searchType)
    url += ('&index='+index)
    if len(endpoint_name) > 0:
        url += ('&embeddingEndpoint='+endpoint_name)
    if len(rerankerEndpoint) > 0:
        url += ('&rerankerEndpoint='+rerankerEndpoint)
    if textSearchNumber > 0:
        url += ('&textSearchNumber='+str(textSearchNumber))
    if vectorSearchNumber > 0:
        url += ('&vectorSearchNumber='+str(vectorSearchNumber))
    if textScoreThresholds > 0:
        url += ('&textScoreThresholds='+str(textScoreThresholds))
    if vectorScoreThresholds > 0:
        url += ('&vectorScoreThresholds='+str(vectorScoreThresholds))
    if len(language) > 0:
        url += ('&language='+language)
    if len(productIdName) > 0:
        url += ('&productIdName='+productIdName)
    if len(description) > 0:
        url += ('&description='+description)
    if len(keywords) > 0:
        url += ('&keywords='+keywords)
    
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
        "https://epr1iwi0jh.execute-api.us-east-1.amazonaws.com/prod",
        key="product_search_invoke_url",
    )
    
    
    sagemaker_endpoint = get_sagemaker_endpoint(search_invoke_url)
    openserch_index = get_openserch_index(search_invoke_url)
    
    product_search_sagemaker_endpoint = st.selectbox("Please Select text embedding sagemaker endpoint",sagemaker_endpoint)
    reranker_sagemaker_endpoint = st.selectbox("Please Select reranker sagemaker endpoint",sagemaker_endpoint)
    index = st.selectbox("Please Select opensearch index",openserch_index)
    
    search_type  = st.radio("Search Type",["text","vector",'mix'])
    st.write('For text search type:')
    textSearchNumber = st.slider("Text Search Number",min_value=1, max_value=10, value=3, step=1)
    textScoreThresholds = st.slider("Text Score Threshold",min_value=0, max_value=50, value=0, step=1)
    
    st.write('For vector search type:')
    vectorSearchNumber = st.slider("Vector Search Number",min_value=1, max_value=10, value=3, step=1)
    vectorScoreThresholds = st.slider("Vector Score Threshold",min_value=0.0, max_value=1.0, value=0.0, step=0.01)
    image_coloum_name = st.text_input(label="Image coloum name", value="mainImage")
    item_name_coloum_name = st.text_input(label="Item coloum name", value="NAME")
    Description_coloum_name = st.text_input(label="Description coloum name", value="SHORT_DESCRIPTION")
    Keywords_coloum_name = st.text_input(label="Keywords coloum name", value="KEYWORDS")

# Add a button to start a new chat
st.sidebar.button("New Query", on_click=new_query, type='primary')

st.session_state.query = st.text_input(label="Please input query", value="")

if st.session_state.query:
    if len(st.session_state.query) ==0:
        st.write("Query is None")
    elif len(search_invoke_url) == 0:
        st.write("Search invoke url is None")
    elif len(product_search_sagemaker_endpoint) == 0:
        st.write("Embedding sagemaker endpoint is None")
    elif len(index) == 0:
        st.write("Opensearch index is None")
        
    elif len(item_name_coloum_name) == 0 and len(Description_coloum_name) == 0 and len(Keywords_coloum_name) == 0:
        st.write("item_name_coloum_name,Description_coloum_name and and Keywords_coloum_name aleast one is not None")
    
    else:
        products = product_search(st.session_state.query,
                                  search_invoke_url,
                                  index,
                                  product_search_sagemaker_endpoint,
                                  reranker_sagemaker_endpoint,
                                  search_type,
                                  textSearchNumber,
                                  vectorSearchNumber,
                                  textScoreThresholds,
                                  vectorScoreThresholds,
                                  productIdName=item_name_coloum_name,
                                  description=Description_coloum_name,
                                  keywords=Keywords_coloum_name
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
            scores_list = []
            rerank_score_list = []
            source_list = []
                
            for product in products:
                score = round(product['score'],3)
                scores_list.append(str(score))
                source = product['source']
                source_list.append(source)
                
                if image_coloum_name in source.keys():
                    image_list.append(source[image_coloum_name])
                    
                if item_name_coloum_name in source.keys():
                    item_name_list.append(source[item_name_coloum_name])
                
                if search_type == 'mix' and len(reranker_sagemaker_endpoint) > 0:
                    reranker_score = round(product['rerank_score'],3)
                    rerank_score_list.append(reranker_score)
                
            with col1:
                for i in range(items_num):
                    col = i % 3
                    if col == 0:
                        if len(item_name_list) > i:
                            name = item_name_list[i]
                            s = f"<p style='font-size:12px;'>{name}</p>"
                            st.markdown(s, unsafe_allow_html=True)
                        if len(image_list) > i:
                            st.image(image_list[i])
                        with st.expander("详情"):
    
                            if len(rerank_score_list) > i:
                                rerank_score = rerank_score_list[i]
                                rerank_score_str = f"<p style='font-size:12px;'>rerank_score:{rerank_score}</p>"
                                st.markdown(rerank_score_str,unsafe_allow_html=True)
                            
                            if len(scores_list) > i:
                                score = scores_list[i]
                                score_str = f"<p style='font-size:12px;'>recall_score:{score}</p>"
                                st.markdown(score_str,unsafe_allow_html=True)
                                
                            if len(source_list) > i:
                                source = source_list[i]
                                for key in source.keys():
                                    value = source[key].strip()
                                    info_str = f"<p style='font-size:12px;'>{key}:{value}</p>"
                                    st.markdown(info_str,unsafe_allow_html=True)
    
            with col2:
                for i in range(items_num):
                    col = i % 3
                    if col == 1:
                        if len(item_name_list) > i:
                            name = item_name_list[i]
                            s = f"<p style='font-size:12px;'>{name}</p>"
                            st.markdown(s, unsafe_allow_html=True)
                        if len(image_list) > i:
                            st.image(image_list[i])
                        with st.expander("详情"):
    
                            if len(rerank_score_list) > i:
                                rerank_score = rerank_score_list[i]
                                rerank_score_str = f"<p style='font-size:12px;'>rerank_score:{rerank_score}</p>"
                                st.markdown(rerank_score_str,unsafe_allow_html=True)
                            
                            if len(scores_list) > i:
                                score = scores_list[i]
                                score_str = f"<p style='font-size:12px;'>recall_score:{score}</p>"
                                st.markdown(score_str,unsafe_allow_html=True)
                                
                            if len(source_list) > i:
                                source = source_list[i]
                                for key in source.keys():
                                    value = source[key].strip()
                                    info_str = f"<p style='font-size:12px;'>{key}:{value}</p>"
                                    st.markdown(info_str,unsafe_allow_html=True)
            with col3:
                for i in range(items_num):
                    col = i % 3
                    if col == 2:
                        if len(item_name_list) > i:
                            name = item_name_list[i]
                            s = f"<p style='font-size:12px;'>{name}</p>"
                            st.markdown(s, unsafe_allow_html=True)
                        if len(image_list) > i:
                            st.image(image_list[i])
                        with st.expander("详情"):
    
                            if len(rerank_score_list) > i:
                                rerank_score = rerank_score_list[i]
                                rerank_score_str = f"<p style='font-size:12px;'>rerank_score:{rerank_score}</p>"
                                st.markdown(rerank_score_str,unsafe_allow_html=True)
                            
                            if len(scores_list) > i:
                                score = scores_list[i]
                                score_str = f"<p style='font-size:12px;'>recall_score:{score}</p>"
                                st.markdown(score_str,unsafe_allow_html=True)
                                
                            if len(source_list) > i:
                                source = source_list[i]
                                for key in source.keys():
                                    value = source[key].strip()
                                    info_str = f"<p style='font-size:12px;'>{key}:{value}</p>"
                                    st.markdown(info_str,unsafe_allow_html=True)