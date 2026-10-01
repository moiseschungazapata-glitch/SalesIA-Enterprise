from fastapi import FastAPI

app = FastAPI(title="SalesIA Enterprise")


@app.get("/health")
def health():
    return {"status": "ok"}
