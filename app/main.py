from fastapi import FastAPI


app = FastAPI(title="TODO")

@app.get("/")
async def index():
    return {"status": "ok"}