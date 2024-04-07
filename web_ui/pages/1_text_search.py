import requests
import streamlit as st
import streamlit.components.v1 as components
import json
from datetime import datetime
import pandas as pd

def product_search(query,
                invoke_url,
                index,
                endpoint_name: str = '',
                searchType: str = 'text',
                textSearchNumber: int = 3,
                vectorSearchNumber: int = 0,
                textScoreThresholds: float = 0,
                vectorScoreThresholds: float = 0,
                language: str = '',
                productIdName: str = ''
                ):
    url = invoke_url + '/text_search?'
    url += ('&query='+query)
    url += ('&searchType='+searchType)
    url += ('&index='+index)
    if len(endpoint_name) > 0:
        url += ('&embeddingEndpoint='+endpoint_name)
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
        "https://gr2nxjp3v4.execute-api.us-east-1.amazonaws.com/prod",
        key="product_search_invoke_url",
    )
    product_search_sagemaker_endpoint = st.text_input(
        "Please input product search sagemaker endpoint",
        "bge-m3-2024-03-31-02-43-25-634-endpoint",
        key="product_search_endpoint",
    )

    index = st.text_input(
        "Please input product search opensearch index",
        "adidas_demo_test_0406_5",
        key="text_search_index",
    )
    
    search_type  = st.radio("Search Type",["text","vector",'mix'])
    st.write('For text search type:')
    textSearchNumber = st.slider("Text Search Number",min_value=1, max_value=10, value=3, step=1)
    textScoreThresholds = st.slider("Text Score Threshold",min_value=0, max_value=50, value=0, step=1)
    
    st.write('For vector search type:')
    vectorSearchNumber = st.slider("Vector Search Number",min_value=1, max_value=10, value=3, step=1)
    vectorScoreThresholds = st.slider("Vector Score Threshold",min_value=0.0, max_value=1.0, value=0.0, step=0.01)

# Add a button to start a new chat
st.sidebar.button("New Query", on_click=new_query, type='primary')

st.session_state.query = st.text_input(label="Please input query", value="")

#if st.button('Product Search'):
if st.session_state.query:
    if len(st.session_state.query) ==0:
        st.write("Query is None")
    elif len(search_invoke_url) == 0:
        st.write("Search invoke url is None")
    elif len(product_search_sagemaker_endpoint) == 0:
        st.write("Embedding sagemaker endpoint is None")
    elif len(index) == 0:
        st.write("Opensearch index is None")
        
    products = product_search(st.session_state.query,
                              search_invoke_url,
                              index,
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
        product_code_list = []
            
        for product in products:
            score = product['score']
            scores_list.append(str(score))
            source = product['source']
            media_url = source['media_url']
            product_name = source['product_name']
            description = source['description_info']
            product_code = source['product_code']
            item_name_list.append(product_name)
            image_list.append(media_url)
            description_list.append(description)
            product_code_list.append(product_code)
            
        with col1:
            for i in range(items_num):
                col = i % 3
                if col == 0:
                    name = item_name_list[i]
                    name_str = f"<p style='font-size:12px;'>{name}</p>"
                    st.markdown(name_str, unsafe_allow_html=True)
                    st.image(image_list[i])
                    with st.expander("详情"):
                        product_code = product_code_list[i]
                        product_code_str = f"<p style='font-size:12px;'>product_code:{product_code}</p>"
                        st.markdown(product_code_str,unsafe_allow_html=True)

                        score = scores_list[i]
                        score_str = f"<p style='font-size:12px;'>score:{score}</p>"
                        st.markdown(score_str,unsafe_allow_html=True)

                        description_info = description_list[i]
                        description_info_str = f"<p style='font-size:12px;'>description_info:{description_info}</p>"
                        st.markdown(description_info_str,unsafe_allow_html=True)
        with col2:
            for i in range(items_num):
                col = i % 3
                if col == 1:
                    name = item_name_list[i]
                    name_str = f"<p style='font-size:12px;'>{name}</p>"
                    st.markdown(name_str, unsafe_allow_html=True)
                    st.image(image_list[i])
                    with st.expander("详情"):
                        product_code = product_code_list[i]
                        product_code_str = f"<p style='font-size:12px;'>product_code:{product_code}</p>"
                        st.markdown(product_code_str,unsafe_allow_html=True)

                        score = scores_list[i]
                        score_str = f"<p style='font-size:12px;'>score:{score}</p>"
                        st.markdown(score_str,unsafe_allow_html=True)

                        description_info = description_list[i]
                        description_info_str = f"<p style='font-size:12px;'>description_info:{description_info}</p>"
                        st.markdown(description_info_str,unsafe_allow_html=True)
        with col3:
            for i in range(items_num):
                col = i % 3
                if col == 2:
                    name = item_name_list[i]
                    name_str = f"<p style='font-size:12px;'>{name}</p>"
                    st.markdown(name_str, unsafe_allow_html=True)
                    st.image(image_list[i])
                    with st.expander("详情"):
                        product_code = product_code_list[i]
                        product_code_str = f"<p style='font-size:12px;'>product_code:{product_code}</p>"
                        st.markdown(product_code_str,unsafe_allow_html=True)

                        score = scores_list[i]
                        score_str = f"<p style='font-size:12px;'>score:{score}</p>"
                        st.markdown(score_str,unsafe_allow_html=True)

                        description_info = description_list[i]
                        description_info_str = f"<p style='font-size:12px;'>description_info:{description_info}</p>"
                        st.markdown(description_info_str,unsafe_allow_html=True)