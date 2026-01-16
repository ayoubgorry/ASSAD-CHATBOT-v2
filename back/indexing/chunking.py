from langchain_text_splitters import RecursiveCharacterTextSplitter

match_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
squad_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=100)

def process_docs(docs):
    for doc in docs:
        if "page_content" in doc.metadata:
            doc.page_content = doc.metadata["page_content"]
            del doc.metadata["page_content"]
    return docs