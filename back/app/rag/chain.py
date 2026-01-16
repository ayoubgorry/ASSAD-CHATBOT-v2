from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from app.rag.retrievers import get_retrievers, format_docs
from app.rag.prompt import PROMPT_TEMPLATE
import os
from dotenv import load_dotenv


load_dotenv()


llm = ChatGoogleGenerativeAI(
    model="gemini-3-pro-preview",
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

static_retriever, matches_retriever = get_retrievers()

def combine_retrievers(query):
    docs_static = static_retriever.invoke(query)
    docs_matches = matches_retriever.invoke(query)
    return format_docs(docs_static + docs_matches)

rag_chain = (
    {"context": combine_retrievers, "question": RunnablePassthrough()}
    | PROMPT_TEMPLATE
    | llm
    | StrOutputParser()
)