import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import MessagesPlaceholder
from langchain.chains.history_aware_retriever import create_history_aware_retriever

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from langchain_community.vectorstores.qdrant import Qdrant
from app.document.services import DocumentsDataService

class AIDataService():
    def get_documents_from_web(self, url):
        loader = PyPDFLoader(url, extract_images=True)
        text = '\n\n'.join([page.page_content for page in loader.load()])
        
        splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=300,
            chunk_overlap=20,
        )

        splitDocs = splitter.split_text(text)

        return splitDocs
    
    def get_client(self):
        client = QdrantClient(
            url="https://42824085-67d1-4a4d-8557-9fff4e673bf9.us-east4-0.gcp.cloud.qdrant.io:6333",
            api_key="B8UzMjVYHhVZznWQQtM9h1rFHPTYzJd6Nl3gfBC-j1sTgwfHuXNniA"
        )
        return client

    def load_qdrant(self, document_edu_name, api_key):
        client = self.get_client()
        qdrant_exit = self.check_document_in_qdrant(client, document_edu_name)

        if qdrant_exit is False:
            client.create_collection(
                collection_name=document_edu_name,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
            )

        return Qdrant(
            client=client,
            collection_name=document_edu_name, 
            embeddings=OpenAIEmbeddings(api_key=api_key)
        ), qdrant_exit
            
    def check_document_in_qdrant(self, client, document_edu_name):
        collections = client.get_collections().collections
        collection_names = [collection.name for collection in collections]

        if document_edu_name not in collection_names:
            return False
        
        return True
        
    def create_db(self, pdf_text, document_edu_name, api_key):
        qdrant, qdrant_exit = self.load_qdrant(document_edu_name, api_key)

        if qdrant_exit is False:
            qdrant.add_texts(pdf_text)

    def create_chain(self, document_edu_name, api_key):
        vectorStore, _ = self.load_qdrant(document_edu_name, api_key)

        llm = ChatOpenAI(
            model='gpt-3.5-turbo',
            temperature=0.3,
            api_key=api_key
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", "Trả lời câu hỏi của user dựa trên context: {context}"),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}")
        ])

        chain = create_stuff_documents_chain(
            llm=llm, 
            prompt=prompt
        )

        retriever = vectorStore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 4}
        )

        retriever_prompt = ChatPromptTemplate.from_messages([
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            ("user", "Với đoạn hội thoại trên, hãy tạo một truy vấn tìm kiếm để lấy thông tin liên quan đến cuộc hội thoại")
        ])

        history_aware_retriever = create_history_aware_retriever(
            llm=llm,
            retriever=retriever,
            prompt=retriever_prompt
        )
        
        retrieval_chain = create_retrieval_chain(
            history_aware_retriever, chain)

        return retrieval_chain

    def process_chat(self, chain, question, chat_history):
        response = chain.invoke({
            "input": question,
            "chat_history": chat_history
        })

        return response["answer"]
        
    def page_pdf_and_build_vector_db(self, url, document_edu_name, document_id, user_id, api_key=None):
        data, code, msg = DocumentsDataService().get_by_purchase(document_id, user_id)
        if (code == 0):
            try:
                if api_key is None:
                    api_key = os.getenv("OPENAI_API_KEY")
                docs = self.get_documents_from_web(url)
                self.create_db(docs, document_edu_name, api_key)
                return None, 0, "Tải tài liệu để đặt câu hỏi thành công"
            except RuntimeError:
                return None, -1, "Tải tài liệu để đặt câu hỏi không thành công"
        else:
            return None, -1, "Bạn chưa thể đặt câu hỏi đối với tài liệu này"

    def chat_with_ai(self, ask, chat_history, document_edu_name, document_id, user_id, api_key=None):
        data, code, msg = DocumentsDataService().get_by_purchase(document_id, user_id)
        if (code == 0):
            try:
                if api_key is None:
                    api_key = os.getenv("OPENAI_API_KEY")

                chain = self.create_chain(document_edu_name, api_key)

                response = self.process_chat(chain, ask, chat_history)
                chat_history.append(HumanMessage(content=ask))
                chat_history.append(AIMessage(content=response))

                return response, 0, "Hỏi thành công"
            except RuntimeError:
                return None, -1, "Hiện tại không thể hỏi được"
        else:
            return None, -1, "Bạn chưa thể đặt câu hỏi đối với tài liệu này"
        
    def thu(self):
        try:
            url = f"https://edushare-s3.s3.amazonaws.com/Transcript_DamThuHang%20trr.pdf"
            return self.get_documents_from_web(url)
        except Exception as e:
            return str(e)