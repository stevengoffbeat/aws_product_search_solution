import requests
import streamlit as st
import streamlit.components.v1 as components
import json
from datetime import datetime
import pandas as pd

def image_search(image_url,invoke_url,endpoint_name):
    url = invoke_url + '/image_search?'
    url += ('&url='+image_url)
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
        "",
        key="image_search_invoke_url",
    )
    image_search_sagemaker_endpoint = st.text_input(
        "Please input image search sagemaker endpoint",
        "",
        key="image_search_endpoint",
    )

# Add a button to start a new chat
st.sidebar.button("New Image", on_click=new_image, type='primary')

st.session_state.url = st.text_input(label="Please input image URL", value="")

if st.button('Image Search'):
    if len(st.session_state.url) ==0:
        st.write("Image url is None")
    elif len(search_invoke_url) == 0:
            st.write("Search invoke url is None")
            
    st.write('输入图片：')
    st.image(st.session_state.url)
            

    if len(image_search_sagemaker_endpoint) == 0:
        st.write("Search sagemaker endpoint is None")
    else:
        products = image_search(st.session_state.url,search_invoke_url,image_search_sagemaker_endpoint)
        
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
                    
