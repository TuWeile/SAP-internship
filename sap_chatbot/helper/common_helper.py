import tiktoken

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader


class CommonHelper:
    @staticmethod
    def text_splitter(chunk_size: int, chunk_overlap: int):
        return RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len
        )

    @staticmethod
    def embedding_cost(chunks, message):
        encoding = tiktoken.encoding_for_model(message.get("modelType"))
        total_tokens = sum([len(encoding.encode(page.page_content)) for page in chunks])
        return f"Total tokens: {total_tokens} | Embedding costs (USD): {total_tokens / 1000 * 0.0004:.6f}"

    @staticmethod
    def document_loader(filepath: str):
        loader = TextLoader(filepath)
        return loader.load()
