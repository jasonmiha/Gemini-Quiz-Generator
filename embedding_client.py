from langchain_google_vertexai import VertexAIEmbeddings

class EmbeddingClient:
    """
    This class initializes a connection to Google Cloud's VertexAI for text embeddings using the
    VertexAIEmbeddings from Langchain. It allows embedding of text queries and documents.
    """
    
    def __init__(self, model_name, project, location):
        """
        Initializes the EmbeddingClient with specific configurations for model name, project, and location.

        :param model_name: A string representing the name of the model to use for embeddings.
        :param project: The Google Cloud project ID where the embedding model is hosted.
        :param location: The location of the Google Cloud project, such as 'us-central1'.
        """
        self.client = VertexAIEmbeddings(
            model_name=model_name,
            project=project,
            location=location
        )
        
    def embed_query(self, query):
        """
        Uses the embedding client to retrieve embeddings for the given query.

        :param query: The text query to embed.
        :return: The embeddings for the query or None if the operation fails.
        """
        vectors = self.client.embed_query(query)
        return vectors
    
    def embed_documents(self, documents):
        """
        Retrieve embeddings for multiple documents.

        :param documents: A list of text documents to embed.
        :return: A list of embeddings for the given documents.
        """
        try:
            return self.client.embed_documents(documents)
        except AttributeError:
            print("Method embed_documents not defined for the client.")
            return None

if __name__ == "__main__":
    model_name = "textembedding-gecko@003"
    project = "ADD-PROJECT-NAME-HERE"
    location = "us-central1"


    vectors = embedding_client.embed_query("Hello World!")
    if vectors:
        print(vectors)
        print("Successfully used the embedding client!")
