import requests
import streamlit as st
import streamlit.components.v1 as components
import json
import time
from datetime import datetime
import pandas as pd
import boto3
from botocore.exceptions import ClientError
import os
import ast
import pandas as pd
import shutil

#region = os.environ.get('AWS_REGION')
#account = os.environ.get('AWS_ACCOUNT_ID')
#print('region:',region)
#print('account:',account)

size = 10

def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        return False
    return True


def split_csv(file_name,output_dir,row_per_file=size):
        chunk_iterator = pd.read_csv(file_name, chunksize=row_per_file)
        file_number = 1
        file_list = []
        for chunk in chunk_iterator:
                new_file_name = f'{output_dir}/data{file_number}.csv'
                chunk.to_csv(new_file_name,index=False)
                file_list.append(new_file_name)
                file_number += 1

        return file_list


def get_sagemaker_endpoint(invoke_url):
    url = invoke_url + '/data_load?'
    url += ('&task=sagemaker_endpoint')
    print('url:',url)
    response = requests.get(url)
    response = ast.literal_eval(response.text)
    print('sagemaker endpoint:',response)
    return response

def get_openserch_index(invoke_url):
    url = invoke_url + '/data_load?'
    url += ('&task=opensearch_index')
    print('url:',url)
    response = requests.get(url)
    response = ast.literal_eval(response.text)
    print('opensearch index:',response)
    return response

def data_load(invoke_url,index,image_coloum_name,endpoint_name,file_name):
    url = invoke_url + '/data_load?'
    url += ('&index='+index)
    if len(image_coloum_name) > 0:
        url += ('&imageColoumName='+image_coloum_name)
    url += ('&task=data_load')
    url += ('&embeddingEndpoint='+endpoint_name)
    url += ('&fileName='+file_name)
    print('url:',url)
    now1 = datetime.now()
    response = requests.get(url)
    now2 = datetime.now()
    print('request task time:',now2-now1)
    response = json.loads(response.text)
    return response

# Re-initialize the chat
def new_file() -> None:
    st.session_state.uploaded_file = ''

    
with st.sidebar:
    invoke_url = st.text_input(
        "Please input a data load api url",
        "",
        key="image_search_invoke_url",
    )
    
    account = st.text_input(
        "Please input aws account:",
        "",
        key="account",
    )
    region = st.text_input(
        "Please input region:",
        "",
        key="region",
    )

    sagemaker_endpoint = get_sagemaker_endpoint(invoke_url)
    openserch_index = get_openserch_index(invoke_url)
    
    image_search_sagemaker_endpoint = st.selectbox("Please Select image embedding sagemaker endpoint",sagemaker_endpoint)
    text_search_sagemaker_endpoint = st.selectbox("Please Select text embedding sagemaker endpoint",sagemaker_endpoint)
    data_opensearch_index = st.selectbox("Please Select opensearch index",openserch_index)

# Add a button to start a new chat
st.sidebar.button("New File", on_click=new_file, type='primary')


new_index = st.text_input("New index","")
image_coloum_name = st.text_input("Image coloum name","")
st.session_state.uploaded_file = st.file_uploader("Upload File",type=['csv'])


if st.session_state.uploaded_file:
    
    index = data_opensearch_index
    if len(new_index) > 0:
        index = new_index

    if len(image_coloum_name) ==0:
        st.write('Image coloum name is None!')

    elif len(index) == 0:
        st.write('Index is None!')

    elif len(account) == 0:
        st.write('account is None!')

    elif len(region) == 0:
        st.write('region is None!')

    else:
        bucket_name = "intelligent-search-data" + "-" + account + "-" + region
        print('name:',st.session_state.uploaded_file.name)
        file_name = st.session_state.uploaded_file.name.split('.')[0] + '-' + str(time.time()) + '.' + st.session_state.uploaded_file.name.split('.')[1]

        data = pd.read_csv(st.session_state.uploaded_file)
        data.to_csv(file_name,index=False)

        data_dir = file_name.split('.')[0]
        os.mkdir(data_dir)
        file_list = split_csv(file_name,data_dir)
        total_number = 0
        total_error_records = []
        if len(file_list) > 0:
            progress_text = "Data is loading to OpenSearch. Please wait."
            my_bar = st.progress(0, text=progress_text)

            with st.empty():
                for percent_complete in range(len(file_list)):
                    split_data = pd.read_csv(file_list[percent_complete])
                    if len(split_data) > 0:
                        split_file_name = file_list[percent_complete]
                        object_name = split_file_name.replace('/','-')
                        upload_file(split_file_name,bucket_name,object_name)

                        response = data_load(invoke_url,index,image_coloum_name,image_search_sagemaker_endpoint,object_name)
                        result = response['result']
                        print("result:",result)
                        records = response['records']
                        error_records = response['error_records']

                        total_number += int(records)
                        st.write('Number of records successfully loaded: ' + str(total_number))

                        if len(total_error_records) > 0:
                            st.write('Error records: ')
                            if len(error_records) > 0:
                                total_error_records.extend(error_records)
                            for record in total_error_records:
                                st.write(record)


                    my_bar.progress(percent_complete + 1, text=progress_text)


        os.remove(file_name)
        shutil.rmtree(data_dir)