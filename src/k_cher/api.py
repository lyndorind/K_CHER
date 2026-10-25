from fastapi import FastAPI, HTTPException

from k_cher import __version__, hello

app = FastAPI(title="K_CHER API", version=__version__)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/version")
def version() -> dict[str, str]:
    return {"version": __version__}


@app.get("/hello/{name}")
def say_hello(name: str) -> dict[str, str]:
    return {"message": hello(name)}


@app.get("/add")
def add(a: float, b: float) -> dict[str, float]:
    return {"result": a + b}


@app.get("/divide")
def divide(a: float, b: float) -> dict[str, float]:
    if b == 0:
        raise HTTPException(status_code=400, detail="Division by zero")
    return {"result": a / b}