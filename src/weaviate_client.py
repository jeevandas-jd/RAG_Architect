
import weaviate
from config import WEAVIATE_URL

def get_client():
    return weaviate.Client(WEAVIATE_URL)
