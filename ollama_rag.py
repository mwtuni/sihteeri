# ollama_rag.py
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_community import embeddings
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain.text_splitter import CharacterTextSplitter

class OllamaRAG:
    def __init__(self, model_name="llama3.2", embedding_model="nomic-embed-text", collection_name="rag-chroma"):
        """
        Initializes the RAG utility for document retrieval and generation using Llama3.2.
        """
        self.llm = ChatOllama(model=model_name)
        self.embedding_model = embeddings.OllamaEmbeddings(model=embedding_model)
        self.collection_name = collection_name
        self.vectorstore = None
        self.retriever = None

    def load_and_split_documents(self, urls):
        """
        Loads documents from specified URLs and splits them for RAG.
        """
        docs = [WebBaseLoader(url).load() for url in urls]
        docs_list = [item for sublist in docs for item in sublist]
        text_splitter = CharacterTextSplitter.from_tiktoken_encoder(chunk_size=7500, chunk_overlap=100)
        return text_splitter.split_documents(docs_list)

    def setup_vectorstore(self, urls):
        """
        Initializes the Chroma vector store with embeddings.
        """
        doc_splits = self.load_and_split_documents(urls)
        self.vectorstore = Chroma.from_documents(documents=doc_splits, collection_name=self.collection_name, embedding=self.embedding_model)
        self.retriever = self.vectorstore.as_retriever()

    def query(self, prompt):
        """
        Performs a RAG query and generates a response.
        """
        if not self.retriever:
            return "Vector store is not set up."

        query_results = self.retriever.invoke(prompt)
        if query_results:
            rag_content = " ".join([doc.page_content for doc in query_results])
        else:
            rag_content = "No relevant content found."

        content_parts = [{"type": "text", "text": rag_content}, {"type": "text", "text": prompt}]
        message = HumanMessage(content=content_parts)
        
        output_parser = StrOutputParser()
        return output_parser.invoke(self.llm.invoke([message]))
