import sys
import os
import streamlit as st
sys.path.append(os.path.abspath('../../'))
from pdf_processing import DocumentProcessor
from embedding_client import EmbeddingClient
import chromadb

# Import Task libraries
from langchain_core.documents import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import Chroma

class ChromaCollectionCreator:
    """
    This class creates a Chroma collection from processed PDF documents using embeddings from Google Cloud's VertexAI.
    It utilizes the DocumentProcessor for document handling and the EmbeddingClient for generating embeddings.
    """
    def __init__(self, processor, embed_model):
        """
        Initializes the ChromaCollectionCreator with a DocumentProcessor instance and embeddings configuration.
        
        :param processor: An instance of DocumentProcessor that has processed documents.
        :param embed_model: An embedding client for embedding documents.
        """
        self.processor = processor      # This will hold the DocumentProcessor
        self.embed_model = embed_model  # This will hold the EmbeddingClient
        self.db = None                  # This will hold the Chroma collection
    
    def create_chroma_collection(self):
        """
        Creates a Chroma collection from the documents processed by the DocumentProcessor instance.
        """
        
        # Check for processed documents
        if len(self.processor.pages) == 0:
            st.error("No documents found!", icon="🚨")
            return

        # Split documents into text chunks
        text_splitter = CharacterTextSplitter(separator="\n", chunk_size=1000, chunk_overlap=200)
        texts = []
        for page in self.processor.pages:
            texts.extend(text_splitter.split_text(page.page_content))
        
        if texts:
            st.success(f"Successfully split pages to {len(texts)} documents!", icon="✅")
        
        # Create the Chroma Collection
        self.db = Chroma.from_texts(texts, embedding=self.embed_model)
        
        if self.db:
            st.success("Successfully created Chroma Collection!", icon="✅")
        else:
            st.error("Failed to create Chroma Collection!", icon="🚨")

    def get_retriever(self):
        """
        Gets the retriever for the Chroma collection.
        
        :return: The retriever for querying the Chroma collection.
        """
        if not self.db:
            raise ValueError("Chroma Collection has not been created yet.")
        return self.db.as_retriever()
    
    def query_chroma_collection(self, query) -> Document:
        """
        Queries the created Chroma collection for documents similar to the query.
        
        :param query: The query string to search for in the Chroma collection.
        :return: The first matching document from the collection with similarity score.
        """
        if self.db:
            docs = self.db.similarity_search_with_relevance_scores(query)
            if docs:
                return docs[0]
            else:
                st.error("No matching documents found!", icon="🚨")
        else:
            st.error("Chroma Collection has not been created!", icon="🚨")

if __name__ == "__main__":
    # Initialize Document Processor
    processor = DocumentProcessor()
    processor.ingest_documents()
    
    # Embedding configuration for VertexAI
    embed_config = {
        "model_name": "textembedding-gecko@003",
        "project": "gemini-quizify-423920",
        "location": "us-central1"
    }
    
    # Initialize Embedding Client
    embed_client = EmbeddingClient(**embed_config)
    
    # Create ChromaCollectionCreator instance
    chroma_creator = ChromaCollectionCreator(processor, embed_client)
    
    with st.form("Load Data to Chroma"):
        st.write("Select PDFs for Ingestion, then click Submit")
        
        # Submit button to trigger Chroma collection creation
        submitted = st.form_submit_button("Submit")
        if submitted:
            chroma_creator.create_chroma_collection()
