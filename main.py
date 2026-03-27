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
            # Phase: Scale Up (60 secs)
            if elapsed >= 60:
                direction = -1
                start_time = time.time()
                await asyncio.sleep(1)
                continue
            
            # Step every 1s until we cross 111,000
            # This ensures we always exceed the 1.1x HPA tolerance
            if load < 111000:
                step = np.random.randint(1, 10001)
                load += step
            await asyncio.sleep(1)
        else:
            # Phase: Scale Down (30 secs)
            if elapsed >= 30:
                direction = 1
                start_time = time.time()
                await asyncio.sleep(1)
                continue
            
            # Step every 1s until we hit the floor (1110)
            if load > 1110:
                step = np.random.randint(5001, 50001)
                load -= step
                if load < 1:
                    load += step
            await asyncio.sleep(1)
            
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
