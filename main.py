from fastapi import FastAPI
from src.controllers.currency_controller import currency_router
from src.controllers.exchange_rates_controller import exchange_rates_router

app = FastAPI(
    title="Currency Exchange API",
    description="REST API для работы с валютами и курсами обмена",
    version="1.0.0"
)

app.include_router(currency_router)
app.include_router(exchange_rates_router)


@app.get("/")
def root():
    """Корневой endpoint"""
    return {
        "message": "Currency Exchange API",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

