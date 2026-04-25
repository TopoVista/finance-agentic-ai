from api.core.config import settings
from api.rag.retriever import get_vector_store


def build_finance_qa_chain(user_id: str):
    from langchain.chains.combine_documents import create_stuff_documents_chain
    from langchain.chains.retrieval import create_retrieval_chain
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_google_genai import ChatGoogleGenerativeAI

    retriever = get_vector_store().as_retriever(
        search_kwargs={"k": 4, "filter": {"user_id": user_id}}
    )
    model = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0.1,
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are Finora's finance assistant. Answer using the provided user transaction context. "
                "Be clear about uncertainty.",
            ),
            ("human", "Question: {input}\n\nContext:\n{context}"),
        ]
    )
    doc_chain = create_stuff_documents_chain(model, prompt)
    return create_retrieval_chain(retriever, doc_chain)
