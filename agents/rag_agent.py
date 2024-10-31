import base64
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_community import embeddings
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain.text_splitter import CharacterTextSplitter

class RAGAgent:
    description = "Retrieves relevant content for text-based queries using RAG."

    def __init__(self, model_name="llama3.2", embedding_model="nomic-embed-text", collection_name="rag-chroma"):
        """
        Initializes the RAGAgent with Llama3.2 model and Chroma vector store for RAG.
        """
        # Set up models for LLM and embeddings
        self.llm = ChatOllama(model=model_name)
        self.embedding_model = embeddings.OllamaEmbeddings(model=embedding_model)
        
        # Initialize vector store and retriever; this will be populated with data as needed
        self.collection_name = collection_name
        self.vectorstore = None
        self.retriever = None

    def load_and_split_documents(self, urls):
        """
        Loads documents from specified URLs and splits them for retrieval-augmented generation (RAG).
        """
        docs = [WebBaseLoader(url).load() for url in urls]
        docs_list = [item for sublist in docs for item in sublist]
        text_splitter = CharacterTextSplitter.from_tiktoken_encoder(chunk_size=7500, chunk_overlap=100)
        return text_splitter.split_documents(docs_list)

    def setup_vectorstore(self, urls):
        """
        Loads documents and initializes the Chroma vector store with embeddings for RAG.
        """
        doc_splits = self.load_and_split_documents(urls)
        self.vectorstore = Chroma.from_documents(documents=doc_splits, collection_name=self.collection_name, embedding=self.embedding_model)
        self.retriever = self.vectorstore.as_retriever()

    def query(self, prompt):
        """
        Queries the RAG agent to retrieve relevant document content and generate a response.
        """
        # Retrieve relevant documents based on the prompt
        query_results = self.retriever.invoke(prompt) if self.retriever else []
        if query_results:
            rag_content = " ".join([doc.page_content for doc in query_results])
        else:
            rag_content = "No relevant content found."

        # Prepare the combined content for LLM response generation
        content_parts = [{"type": "text", "text": rag_content}, {"type": "text", "text": prompt}]
        message = HumanMessage(content=content_parts)

        # Use the LLM to process the combined content
        output_parser = StrOutputParser()
        response = output_parser.invoke(self.llm.invoke([message]))
        return response

# Example Usage
if __name__ == "__main__":
    agent = RAGAgent()
    urls = ["http://127.0.0.1:8088/menub.txt"]
    agent.setup_vectorstore(urls)
    prompt = "Provide detailed information on 31.10.2024 menu."
    print(agent.query(prompt))
