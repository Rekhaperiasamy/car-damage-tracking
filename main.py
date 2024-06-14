from fastapi import FastAPI
from routers import car, damage, report

app = FastAPI()

app.include_router(car.router)
app.include_router(damage.router)
app.include_router(report.router)
