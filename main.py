import asyncio
import uvicorn
import numpy as np
import time
import math
from fastapi import FastAPI
from prometheus_client import make_asgi_app, Gauge

app = FastAPI()
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Custom Metric
simulated_user_load = Gauge('simulated_user_load', 'Simulated user load using Poisson distribution')

async def update_metrics():
    while True:
        # Generate a simple value between 1 and 9 for predictable scaling
        load = np.random.randint(1, 10)
        simulated_user_load.set(load)
        print(f"simulated_user_load: {load}", flush=True)
        await asyncio.sleep(5)
        
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(update_metrics())

@app.get("/value")
def get_value():
    # Helper to get the current value without parsing Prometheus format
    return float(simulated_user_load._value.get())

@app.get("/")
def read_root():
    return {"status": "running", "metric": "simulated_user_load"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
