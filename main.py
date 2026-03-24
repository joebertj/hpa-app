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
    load = 1
    direction = 1  # 1 for up, -1 for down
    start_time = time.time()
    
    while True:
        elapsed = time.time() - start_time
        
        if direction == 1:
            # Phase: Scale Up (3 mins)
            if elapsed >= 180:
                direction = -1
                start_time = time.time()
                await asyncio.sleep(5)
                continue
            
            # Step every 5s
            step = np.random.randint(1, 10001)
            load += step
            await asyncio.sleep(5)
        else:
            # Phase: Scale Down (2 mins)
            if elapsed >= 120:
                direction = 1
                start_time = time.time()
                await asyncio.sleep(2)
                continue
            
            # Step every 2s
            step = np.random.randint(1, 10001) * multiplier
            load -= step
            load = max(1, load)
            await asyncio.sleep(2)
            
        simulated_user_load.set(load)
        print(f"simulated_user_load: {int(load)}", flush=True)
        
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
