from langchain.vectorstores import Pinecone

import pinecone
from langchain_community.embeddings import OpenAIEmbeddings


class PineconeHelper:
    def __init__(self, message):
        self.message = message

        self.api_key = message.get("pineconeKey")
        self.environment = message.get("pineconeEnv")

    def initialize(self):
        pinecone.init(api_key=self.api_key, environment=self.environment)
        return pinecone.version()

    @staticmethod
    def list_index():
        return pinecone.list_indexes()

    @staticmethod
    def describe_index(index_name: str):
        return pinecone.describe_index(index_name)

    def describe_index_stats(self, index_name):
        if index_name in self.list_index():
            index = pinecone.Index(index_name)
            return index.describe_index_stats()
        else:
            return None

    def add_index(self, index_name: str):
        if index_name not in self.list_index():
            pinecone.create_index(index_name, dimension=1536, metric="cosine")
            return True
        else:
            return False

    def del_index(self, index_name: str):
        if index_name in self.list_index():
            pinecone.delete_index(index_name)
            return True
        else:
            return False

    def del_all_index(self):
        indexes = self.list_index()
        for i in indexes:
            pinecone.delete_index(i)

    def put_vectors_in_index(self, index_name: str, vecs, ids: list):
        if index_name in self.list_index():
            index = pinecone.Index(index_name)
            return index.upsert(vectors=zip(vecs, ids))
        else:
            return None

    def get_vectors_from_index(self, index_name: str, ids: list):
        if index_name in self.list_index():
            index = pinecone.Index(index_name)
            return index.fetch(ids=ids)
        else:
            return None

    def get_embeddings_from_index(self, index_name):
        embedding = OpenAIEmbeddings()

        if index_name in self.list_index():
            return Pinecone.from_existing_index(index_name, embedding)

    def del_vectors_from_index(self, index_name: str, ids: list):
        if index_name in self.list_index():
            index = pinecone.Index(index_name)
            index.delete(ids=ids)
            return True
        else:
            return False

    def del_all_vectors_in_index(self, index_name: str, ids: list):
        if index_name in self.list_index():
            index = pinecone.Index(index_name)
            index.delete(delete_all=True)
            return True
        else:
            return False

    def get_query_top_vectors_from_index(self, index_name: str, query, val: int):
        if index_name in self.list_index():
            index = pinecone.Index(index_name)
            return index.query(queries=query, top_k=val, include_values=False)
        else:
            return None

    def put_doc_chunks_in_index(self, chunks, embeddings, index_name: str):
        if not embeddings:
            embeddings = OpenAIEmbeddings()

        if index_name in self.list_index():
            return Pinecone.from_documents(chunks, embeddings, index_name=index_name)
        else:
            return None
