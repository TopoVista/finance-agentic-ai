from api.core.config import settings


def get_vector_store():
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    from langchain_chroma import Chroma

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        google_api_key=settings.GOOGLE_API_KEY,
    )
    return Chroma(
        collection_name="finora-finance-knowledge",
        embedding_function=embeddings,
        persist_directory=settings.CHROMA_PERSIST_DIR,
    )
