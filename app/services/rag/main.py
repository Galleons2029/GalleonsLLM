import os, logging, qdrant_client
from llama_index.core.llms import ChatMessage
from llama_index.llms.openai_like import OpenAILike

from llama_index.core import StorageContext, Settings, VectorStoreIndex, SimpleDirectoryReader
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.fastembed import FastEmbedEmbedding
import litserve as ls

class DocumentChatAPI(ls.LitAPI):

    def setup(self, device):
        Settings.llm = OpenAILike(model="qwen2-pro", api_base="http://192.168.100.111:8001/v1/", api_key="dummy")
        Settings.embed_model = FastEmbedEmbedding(model_name="BAAI/bge-small-zh-v1.5")
        client = qdrant_client.QdrantClient(host="localhost", port=6333)

        vector_store = QdrantVectorStore(client=client, collection_name="doc_search_collection")
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        documents = SimpleDirectoryReader(input_dir="../../tests/docs").load_data()
        index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
        self.query_engine = index.as_query_engine()

    def decode_request(self, request):
        return request["query"]

    def predict(self, query):
        return self.query_engine.query(query)

    def encode_response(self, output):
        return {"output": output}

if __name__ == "__main__":
    api = DocumentChatAPI()
    server = ls.LitServer(api)
    server.run(port=9001)