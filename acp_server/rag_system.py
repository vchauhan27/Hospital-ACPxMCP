import faiss  # Add this at the very top
print(f"FAISS version: {faiss.__version__}")  # Verify installation

from collections.abc import AsyncGenerator
from acp_sdk.models import Message, MessagePart
from acp_sdk.server import RunYield, RunYieldResume, Server
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import nest_asyncio
import os
from dotenv import load_dotenv

os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

load_dotenv()
nest_asyncio.apply()

class PolicyRAGSystem:
    def __init__(self):
        self.file_path = r"C:\Users\LENOVO\OneDrive\Desktop\ACPxMCP\hospital.pdf"
        self.vectorstore_path = r"C:\Users\LENOVO\OneDrive\Desktop\ACPxMCP\vectorstore"
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2"
        )
        
        self.llm = ChatGroq(
            temperature=0.3,
            model_name="llama3-8b-8192",
            api_key=os.getenv("GROQ_API_KEY")
        )
        
        self.vectorstore = self._initialize_vectorstore()
        self.chain = self._create_chain()

    def _initialize_vectorstore(self):
        if os.path.exists(self.vectorstore_path):
            return FAISS.load_local(
                self.vectorstore_path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
        
        loader = PyPDFLoader(self.file_path)
        pages = loader.load_and_split()
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1200,
            chunk_overlap=200
        )
        texts = text_splitter.split_documents(pages)
        
        vectorstore = FAISS.from_documents(texts, self.embeddings)
        vectorstore.save_local(self.vectorstore_path)
        return vectorstore
    
    def _create_chain(self):
        prompt = ChatPromptTemplate.from_template(
            """You are an insurance policy expert. Answer the user's question
            based only on the following context. Be precise and professional:
            
            Context: {context}
            
            Question: {question}
            
            Answer:"""
        )
        return prompt | self.llm | StrOutputParser()

    def query(self, question: str) -> str:
        docs = self.vectorstore.similarity_search(question, k=3)
        context = "\n\n".join([doc.page_content for doc in docs])
        return self.chain.invoke({"question": question, "context": context})

server = Server()
rag_system = PolicyRAGSystem()

@server.agent()
async def policy_agent(input: list[Message]) -> AsyncGenerator[RunYield, RunYieldResume]:
    """Insurance policy coverage agent using RAG and Groq's LLM"""
    user_question = input[0].parts[0].content
    
    try:
        response = rag_system.query(user_question)
        yield Message(parts=[MessagePart(content=response)])
        
    except Exception as e:
        error_msg = f"Error processing request: {str(e)}"
        yield Message(parts=[MessagePart(content=error_msg)])

if __name__ == "__main__":
    print("Starting Policy Agent Server on port 8001...")
    server.run(port=8001)