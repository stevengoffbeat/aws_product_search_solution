import requests
import streamlit as st
import streamlit.components.v1 as components
import json
from datetime import datetime
import pandas as pd

def get_protential_tags(image_url,protential_tags,invoke_url,endpoint_name):
    url = invoke_url + '/image_search?'
    url += ('&url='+image_url)
    url += ('&task=classification')
    url += ('&protentialTags='+protential_tags)
    url += ('&embeddingEndpoint='+endpoint_name)
    
    print('url:',url)
    response = requests.get(url)
    result = response.text
    result = json.loads(result)
    print("result:",result)
    tag_confidentials = result['tagConfidentials']
    
    return tag_confidentials


# Re-initialize the chat
def new_image() -> None:
    st.session_state.url = ''
    
with st.sidebar:

    search_invoke_url = st.text_input(
        "Please input a image tag api url",
        "",
        key="image_search_invoke_url",
    )
   
    image_tags_sagemaker_endpoint = st.text_input(
        "Please input image tags sagemaker endpoint",
        "",
        key="image_tags_endpoint",
    )
    threshold = st.slider("Tag threshold",min_value=0, max_value=1, value=0.5, step=0.01)

# Add a button to start a new chat
st.sidebar.button("New Image", on_click=new_image, type='primary')

st.session_state.url = st.text_input(label="Please input image URL", value="")

if st.button('Image Tags'):
    if len(st.session_state.url) ==0:
        st.write("Image url is None")
    elif len(search_invoke_url) == 0:
            st.write("Search invoke url is None")
            
    st.write('输入图片：')
    st.image(st.session_state.url)
            
    
    if len(image_tags_sagemaker_endpoint) == 0:
        st.write("Iamge tags sagemaker endpoint is None")
    else:

        protential_tags_list = [
            "white,black,green,pink,blue,gold,organge,gray,brown,red",
            "Low Tops,High Top,No heel",
            "Hole Shoes,Sandals,Half Slippers,Beach Shoes,Sneakers,Running Shoes,Canvas Shoes,Water Shoes,Hiking Shoes",
            "Flat Bottom,Thick Bottom,Rubber Sole,Mesh Surface,Drain Hole,Anti-Slippery,Non-slip Soles,Hollow,Plastic"
        ]
        
        for protential_tags in protential_tags_list:
            tag_confidentials = get_protential_tags(st.session_state.url,protential_tags,search_invoke_url,image_tags_sagemaker_endpoint)
            
            st.write('tag confidentials:')
            category = [tag for tag in tag_confidentials if tag_confidentials[tag] > threshold]
        
            tags = list(tag_confidentials.keys())
            scores = [round(score,3) for score in tag_confidentials.values()]
            data = {
                "category": tags,
                "scores": scores
            }
            df = pd.DataFrame(data)
            st.dataframe(df)
            st.write('Category:')
            st.write(category)
            st.write('--------------------------------')
       