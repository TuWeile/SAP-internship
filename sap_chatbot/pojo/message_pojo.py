import os

#from dotenv import load_dotenv, find_dotenv


class MessagePojo:
    """
    Message POJO object for handling of environment or system variables.
    """
    # Disabled to prevent API keys from being hard-coded
    # load_dotenv("./config/.env", override=True)

    def __init__(self):
        self.openAIKey = os.environ.get("OPENAI_API_KEY") or None
        self.pineconeKey = os.environ.get("PINECONE_API_KEY") or None
        self.pineconeEnv = os.environ.get("PINECONE_ENV") or None

        self.llmType = "openai"
        self.modelType = "gpt-3.5-turbo-1106"
        self.referenceFile = "./data/profile.txt"
        self.indexName = "sap-assignment"

        self.chunkSize = 512
        self.chunkOverlap = 32
        self.kValue = 5

    def to_json(self):
        """
        Generates a JSON / dict output from the MessagePojo attributes.
        :return:  A dict object: a JSON version of the message POJO structure.
        """
        return vars(self)
