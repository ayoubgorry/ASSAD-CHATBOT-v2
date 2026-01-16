from fastapi import FastAPI
from pydantic import BaseModel
from app.rag.chain import rag_chain
from app.rag.query_expander import expand_query
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="CAN 2025 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # DEV ONLY
    allow_credentials=False,  # IMPORTANT avec *
    allow_methods=["*"],
    allow_headers=["*"],
)

class Question(BaseModel):
    query: str

@app.post("/chat")
async def chat(question: Question):
    try:
        refined_query = expand_query(question.query)
        response = rag_chain.invoke(refined_query) 
        return {"response": response}
    except Exception as e:
        return {"response": f"Erreur technique : {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)