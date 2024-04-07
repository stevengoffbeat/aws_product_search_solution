import streamlit as st

st.set_page_config(
    page_title = 'aws search solution'
)

st.write('# AWS Product Search Solution')

st.markdown(
    """
    AWS Product Search Solution 是一个提升电商商品搜索结果的解决方案，主要特征包括：
    ### 商品搜索
    - 文本搜索：通过用户输入的query文本与商品描述文本的匹配进行搜索
    - 向量搜索：通过计算用户输入的query文本向量与商品描述文本向量的向量相似度进行搜索
    - 混合搜索：同时支持文本搜索和向量搜索
    
    ### 图片搜索
    - 向量搜索：通过计算用户输入图片向量与商品图片向量的向量相似度进行搜索

    ### 图片打标
    - 向量打标：通过计算用户输入图片向量与标签信息向量的向量相似度进行搜索
    
    """
)