from storages.backends.azure_storage import AzureStorage
import os
from dotenv import load_dotenv

load_dotenv()

class AzureMediaStorage(AzureStorage):
    account_name = os.getenv('STATIC_AZURE_ACCOUNT_NAME') # Must be replaced by your <storage_account_name>
    account_key = os.getenv('STATIC_AZURE_ACCOUNT_KEY') # Must be replaced by your <storage_account_key>
    azure_container = 'media'
    expiration_secs = None

class AzureStaticStorage(AzureStorage):
    account_name = os.getenv('STATIC_AZURE_ACCOUNT_NAME') # Must be replaced by your <storage_account_name>
    account_key = os.getenv('STATIC_AZURE_ACCOUNT_KEY') # Must be replaced by your <storage_account_key>
    azure_container = 'static'
    expiration_secs = None