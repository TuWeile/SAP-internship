import os

from langchain_community.embeddings import OpenAIEmbeddings

from helper.base_handler import BaseHandler
from helper.pinecone_helper import PineconeHelper
from src.llm.model_handler import ModelHandler


class AppHandler(BaseHandler):
    def __init__(self, message: dict, logfile):
        super().__init__(message, logfile)

        self.model_handler = ModelHandler(message, logfile)
        self.pinecone = PineconeHelper(self.message)

        self.chunks = None
        self.reference = None

        self.chat_history = list()
        self.initialized = False
        self.data_store = None

        os.environ["OPENAI_API_KEY"] = self.message.get("openAIKey")

    def main(self) -> bool:
        try:
            if not self.initialized:
                self.pinecone.initialize()
                model = self.model_handler.get_model_factory()
                self.initialized = True

            if not self.data_store:
                self.data_store = self.pre_actions()

            if self.data_store:
                self.logger.info(f"vector_store received from database. Starting up model.")
                answer, self.chat_history = self.model_handler.get_response_ss_with_memory(
                    query="Who are you?",
                    vector_store=self.data_store,
                    keywords=self.message.get("kValue"),
                    chat_history=self.chat_history
                )
                if answer:
                    self.done = True
            else:
                self.logger.error("Unable to build new vector embeddings for model. Terminating.")
                raise Exception("No embeddings received.")

        except Exception as e:
            self.logger.error(f"Exception encountered in main method of AppHandler: [{e}]")
        finally:
            return self.done

    def pre_actions(self):
        try:
            self.logger.info(self.message)
            if not self.initialized:
                self.pinecone.initialize()
                model = self.model_handler.get_model_factory()
                self.initialized = True

            if self.message.get("indexName") not in self.pinecone.list_index():
                self.logger.info(f"{self.message.get('indexName')} index not found. Creating and adding vectors.")

                with open(self.message.get("referenceFile")) as f:
                    self.reference = f.read()

                function = self.helper.text_splitter(self.message.get("chunkSize", 256),
                                                     self.message.get("chunkOverlap", 20))
                self.chunks = function.create_documents([self.reference])

                self.logger.debug(self.helper.embedding_cost(self.chunks, self.message))

                self.pinecone.add_index(self.message.get("indexName"))

                vectors_obj = self.pinecone.put_doc_chunks_in_index(self.chunks,
                                                                    OpenAIEmbeddings(
                                                                        openai_api_key=self.message.get("openAIKKey")),
                                                                    self.message.get("indexName"))

            else:
                self.logger.info(f"{self.message.get('indexName')} index found. Loading embeddings.")
                vectors_obj = self.pinecone.get_embeddings_from_index(self.message.get("indexName"))
                self.data_store = vectors_obj

            return vectors_obj

        except Exception as e:
            self.logger.warning(f"Exception encountered in pre_actions method of AppHandler: [{e}]")
            return None

    def rebuild_embeddings(self):
        try:
            self.logger.info(self.message)
            if not self.initialized:
                self.pinecone.initialize()
                model = self.model_handler.get_model_factory()
                self.initialized = True

            if self.message.get("indexName") in self.pinecone.list_index():
                completed = self.pinecone.del_index(self.message.get("indexName"))
                if completed:
                    self.logger.info("Index has been deleted.")
                else:
                    self.logger.info("Failed to delete index.")

        except Exception as e:
            self.logger.warning(f"Exception encountered in rebuild_embeddings method of AppHandler: [{e}]")
