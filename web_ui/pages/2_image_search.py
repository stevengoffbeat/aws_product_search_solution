import requests
import streamlit as st
import streamlit.components.v1 as components
import json
from datetime import datetime
import pandas as pd

def image_search(image_url,index,invoke_url,endpoint_name):
    url = invoke_url + '/image_search?'
    url += ('&url='+image_url)
    url += ('&index='+index)
    url += ('&task=image-search')
    url += ('&embeddingEndpoint='+endpoint_name)
    
    print('url:',url)
    response = requests.get(url)
    result = response.text
    result = json.loads(result)
    print("result:",result)
    products = result['products']

    return products



# Re-initialize the chat
def new_image() -> None:
    st.session_state.url = ''
    
with st.sidebar:

    search_invoke_url = st.text_input(
        "Please input a image search api url",
        "https://u9rpcxlh3c.execute-api.us-east-1.amazonaws.com/prod",
        key="image_search_invoke_url",
    )
    image_search_sagemaker_endpoint = st.text_input(
        "Please input image search sagemaker endpoint",
        "image-embedding-clip-vit-base-patch32-2024-04-06-14-59-49-269",
        key="image_search_endpoint",
    )

    index = st.text_input(
        "Please input image search opensearch index",
        "adidas_demo_test_0406_5",
        key="image_search_index",
    )

# Add a button to start a new chat
st.sidebar.button("New Image", on_click=new_image, type='primary')

st.session_state.url = st.text_input(label="Please input image URL", value="")

#if st.button('Image Search'):
if st.session_state.url:
    if len(st.session_state.url) ==0:
        st.write("Image url is None")
    elif len(search_invoke_url) == 0:
        st.write("Search invoke url is None")
    elif len(index) == 0:
        st.write("Opensearch index is None")
            
    st.write('输入图片：')
    st.image(st.session_state.url)
            

    if len(image_search_sagemaker_endpoint) == 0:
        st.write("Search sagemaker endpoint is None")
    else:
        products = image_search(st.session_state.url,index,search_invoke_url,image_search_sagemaker_endpoint)
        
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

                            score = product_code_list[i]
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

                            score = product_code_list[i]
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

                            score = product_code_list[i]
                            score_str = f"<p style='font-size:12px;'>score:{score}</p>"
                            st.markdown(score_str,unsafe_allow_html=True)

                            description_info = description_list[i]
                            description_info_str = f"<p style='font-size:12px;'>description_info:{description_info}</p>"
                            st.markdown(description_info_str,unsafe_allow_html=True)