from app.core.config import USE_OPENAI, OPENAI_API_KEY, HUGGINGFACE_MODEL_NAME, HUGGINGFACEHUB_API_TOKEN
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_community.chat_models import ChatOpenAI
from langchain_huggingface import HuggingFaceEndpoint
import os

class DocumentQA:
    def __init__(self, index_path="data/vectorstore/index"):
        self.index_path = index_path
        self.vectorstore = None
        self.retriever = None
        self.qa_chain = None
        self.embeddings = self._load_embeddings()
        self.llm = self._load_llm()

    def _load_embeddings(self):
        if USE_OPENAI:
            return OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        else:
            return HuggingFaceEmbeddings(model_name=HUGGINGFACE_MODEL_NAME)

    def _load_llm(self):
        if USE_OPENAI:
            return ChatOpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)
        else:
            return HuggingFaceEndpoint(
                repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1",
                huggingfacehub_api_token=HUGGINGFACEHUB_API_TOKEN,
                temperature=0.1
            )

    def load_and_index_pdf(self, file_path):
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        docs = splitter.split_documents(documents)

        self.vectorstore = FAISS.from_documents(docs, self.embeddings)
        self.vectorstore.save_local(self.index_path)
        self.retriever = self.vectorstore.as_retriever()
        self.qa_chain = RetrievalQA.from_chain_type(llm=self.llm, retriever=self.retriever)

    def load_existing_index(self):
        if os.path.exists(self.index_path):
            self.vectorstore = FAISS.load_local(self.index_path, self.embeddings)
            self.retriever = self.vectorstore.as_retriever()
            self.qa_chain = RetrievalQA.from_chain_type(llm=self.llm, retriever=self.retriever)
            return True
        return False

    def ask(self, question):
        if not self.qa_chain:
            raise ValueError("Index not loaded. Please load documents first.")
        return self.qa_chain.invoke({"query": question})
