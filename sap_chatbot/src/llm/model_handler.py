import os

from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain_community.embeddings import OpenAIEmbeddings

from helper.base_handler import BaseHandler


class ModelHandler(BaseHandler):
    def __init__(self, message, logfile):
        super().__init__(message, logfile)
        self.model = None
        self.chain = None

        os.environ["OPENAI_API_KEY"] = self.message.get("openAIKey")

    def get_model_factory(self):

        llm_type = self.message.get("llmType")
        model_type = self.message.get("modelType")

        if llm_type == "openai":
            self.logger.info(f"Selected LLM type [{llm_type}] and model type [{model_type}]")
            try:
                self.model = ChatOpenAI(model_name=model_type, temperature=0.7, max_tokens=128,
                                        openai_api_key=self.message.get("openAIKKey"))
                self.logger.info(f"Model allocated and parameters [{self.model}]")
            except Exception as e:
                self.logger.warning(f"Exception encountered in get_model_factory function: [{e}]")

        else:
            self.logger.warning(f"Unsupported LLM type [{llm_type}] has been provided. Returning null value.")

        return self.model

    def get_embeddings(self, chunks):
        embedding = OpenAIEmbeddings()
        result = list()
        total_chunks = len(chunks)

        for number in range(total_chunks):
            self.logger.debug(f"Commencing vector embedding of chunks {number}: {chunks[number].page_content}")
            vector = embedding.embed_query(chunks[number].page_content)
            result.append(vector)

        return result

    def get_response_ss(self, query: str, vector_store):
        self.logger.info(f"Querying vector store with query [{query}]")
        try:
            best_fit = vector_store.similarity_search(query)

            if best_fit:
                self.logger.debug(f"Results from best fit chunks include {len(best_fit)} best chunks.")
                if not self.model:
                    self.logger.warning(f"Model has not been initialized yet. Please initialize a model first!")
                    raise Exception("No model provided, run get_model_factory method first.")

                retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={'k': 3})
                chain = RetrievalQA.from_chain_type(llm=self.model, chain_type="stuff", retriever=retriever)
                return chain.run(query)
            else:
                self.logger.debug(f"No results obtained from best fit chunks. Closing off function.")
                return None

        except Exception as e:
            self.logger.warning(f"Exception encountered in get_response_ss from ModelHandler: [{e}]")

    def get_response_ss_with_memory(self, query, vector_store, keywords, chat_history):
        if chat_history is None:
            chat_history = list()

        try:
            retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={'k': keywords})
            cr_chain = ConversationalRetrievalChain.from_llm(self.model, retriever)
            result = cr_chain({"question": query, "chat_history": chat_history})
            chat_history.append((query, result["answer"]))

            return result, chat_history

        except Exception as e:
            self.logger.warning(f"Exception encountered in get_response_ss_with_memory from ModelHandler: [{e}]")

    def get_response_ss_with_memory_streamlit(self, query, vector_store, keywords, chat_history):
        if chat_history is None:
            chat_history = list()

        try:
            retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={'k': keywords})
            if not self.model:
                self.model = self.get_model_factory()
            cr_chain = ConversationalRetrievalChain.from_llm(self.model, retriever)
            result = cr_chain({"question": query, "chat_history": chat_history})
            chat_history.append((query, result["answer"]))

            return [result, chat_history]

        except Exception as e:
            self.logger.warning(f"Exception encountered in get_response_ss_with_memory from ModelHandler: [{e}]")
