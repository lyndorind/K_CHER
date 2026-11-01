import asyncio
import math
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Path, Query, Response
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from k_cher import __version__, hello
from k_cher.config import get_database_url
from k_cher.db import get_db, init_db
from k_cher.models import Calculation
from k_cher.schemas import CalculationCreate, CalculationRead


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    # Таблиці створюються лише тоді, коли базу налаштовано (у Docker/Compose).
    if get_database_url() is not None:
        await asyncio.to_thread(init_db)
    yield


app = FastAPI(title="K_CHER API", version=__version__, lifespan=lifespan)

DbSession = Annotated[Session, Depends(get_db)]
CalculationId = Annotated[int, Path(ge=1, le=2_147_483_647)]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def ready(db: DbSession) -> dict[str, str]:
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc
    return {"status": "ready"}


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


def _calculate(operation: str, a: float, b: float) -> float:
    if operation == "add":
        result = a + b
    else:  # "divide": інші значення відсікає схема CalculationCreate
        if b == 0:
            raise HTTPException(status_code=400, detail="Division by zero")
        result = a / b
    if not math.isfinite(result):
        raise HTTPException(status_code=400, detail="Result is out of range")
    return result


def _get_or_404(db: Session, calculation_id: int) -> Calculation:
    record = db.get(Calculation, calculation_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return record


@app.post("/calculations", status_code=201, response_model=CalculationRead)
def create_calculation(payload: CalculationCreate, db: DbSession) -> Calculation:
    result = _calculate(payload.operation, payload.a, payload.b)
    record = Calculation(
        operation=payload.operation, a=payload.a, b=payload.b, result=result
    )
    db.add(record)
    db.commit()
    return record


@app.get("/calculations", response_model=list[CalculationRead])
def list_calculations(
    db: DbSession,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[Calculation]:
    statement = select(Calculation).order_by(Calculation.id.desc()).limit(limit)
    return list(db.scalars(statement))


@app.get("/calculations/{calculation_id}", response_model=CalculationRead)
def get_calculation(calculation_id: CalculationId, db: DbSession) -> Calculation:
    return _get_or_404(db, calculation_id)


@app.delete("/calculations/{calculation_id}", status_code=204)
def delete_calculation(calculation_id: CalculationId, db: DbSession) -> Response:
    db.delete(_get_or_404(db, calculation_id))
    db.commit()
    return Response(status_code=204)
