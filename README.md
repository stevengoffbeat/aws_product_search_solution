# Deployment guide

### 0.Create EC2 instance

(1)	input name, such as ‘product_search’
(2)	Instance type select t3.large
(3)	Create new Key pair
(4)	In the Network setting, select ‘Allow HTTP traffic from the internet’
(5)	In the configure storge, input ‘20’ GiB
(6)	In the Advanced details, click ‘Create new IAM profile’
    a.In the IAM Role page, click Create role
    b.In the Select trusted entity page, select EC2 in the Use case and click next
    c.Select role:
        •	AmazonOpenSearchServiceFullAccess
        •	AmazonS3FullAccess
        •	AmazonSageMakerFullAccess
        •	AWSCloudFormationFullAccess
        •	SecretsManagerReadWrite
    d.Select the role in the IAM instance profile
(7)	Launch the EC2 and Connect the EC2
(8) download the code from git
```
sudo yum update
sudo yum install git
git clone https://github.com/paulhebo/aws_product_search_solution.git
```


### 1. Lambda and OpenSearch deployment

Deploy resources with reference to ./deployment/README.md


### 2. model deployment

In the Amazon SageMaker -> Notebook instances -> SearchGuideNotebook

* open clip_classification_deploy/deploy-clip-model-on-sagemaker.ipynb to deploy the image tagging model

* open clip_image_embedding_deploy/deploy-clip-image-embedding.ipynb to deploy the image search model

* open text_embedding_deploy/text_embedding_deploy to deploy the text search model

* open rerank_model_deploy/bge_m3_reranker_deploy.ipynb to deploy the reranker model


### 3. webUI deployment


Deploy webUI with reference to ./web_ui/Deploy streamlit in EC2.md


### 4. Online data load

In the the web ui page, open data_load page to load data. 


### 5. Offline data load

In the Amazon SageMaker -> Notebook instances -> SearchGuideNotebook

* open data_load/data_load_csv_text.ipynb to load the product information with csv format

* open data_load/data_load_csv_image.ipynb to load the product information inclue image with csv format

* open data_load/data_load_csv_json.ipynb to load the product information with csv json
