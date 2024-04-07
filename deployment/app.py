import os
import aws_cdk as cdk
from lib.ss_image_search_stack import ImageSearchStack
from lib.ss_text_search_stack import TextSearchStack
from lib.ss_search_notebook import SearchNotebookStack
from lib.ss_opensearch_stack import ProductOpenSearchStack


ACCOUNT = os.getenv('AWS_ACCOUNT_ID', '')
REGION = os.getenv('AWS_REGION', '')
AWS_ENV = cdk.Environment(account=ACCOUNT, region=REGION)
env = AWS_ENV
print(env)
app = cdk.App()

image_search_stack = ImageSearchStack(app, "ImageSearchStack",env=env)
text_search_stack = TextSearchStack(app, "TextSearchStack",env=env)
search_notebook_stack = SearchNotebookStack(app, "SearchNotebookStack", env=env)
product_opensearch_stack = ProductOpenSearchStack(app, "ProductOpenSearchStack", env=env)

app.synth()