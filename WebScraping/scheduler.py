from fastapi import FastAPI, APIRouter, Request
from fastapi.responses import JSONResponse
from apscheduler.schedulers.background import BackgroundScheduler
import os
import subprocess
import logging

app = FastAPI(title="Scheduler and API Service")
router = APIRouter()
scheduler = BackgroundScheduler()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to run all scraping scripts in the folder
def run_scripts():
    folder_path = './scraping_scripts/'  # Update this path as needed
    if not os.path.exists(folder_path):
        logging.error(f"Folder path '{folder_path}' does not exist.")
        return

    logging.info("Starting to run scraping scripts...")
    for filename in os.listdir(folder_path):
        if filename.endswith('.py'):
            filepath = os.path.join(folder_path, filename)
            logging.info(f"Running script: {filename}")
            try:
                subprocess.run(['python', filepath], check=True)
            except subprocess.CalledProcessError as e:
                logging.error(f"Error running script {filename}: {e}")
    logging.info("Finished running all scripts.")

# Scheduler job
scheduler.add_job(run_scripts, 'cron', hour=0, minute=0)  # Adjust the timing as needed
scheduler.start()

@app.get("/")
async def index():
    return {"message": "Welcome to the FastAPI Scheduler API"}

@app.post("/start_scheduler")
async def start_scheduler():
    if not scheduler.running:
        scheduler.start()
        logging.info("Scheduler started")
        return {"message": "Scheduler started"}
    return JSONResponse(status_code=400, content={"message": "Scheduler is already running"})

@app.post("/stop_scheduler")
async def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logging.info("Scheduler stopped")
        return {"message": "Scheduler stopped"}
    return JSONResponse(status_code=400, content={"message": "Scheduler is not running"})

@app.post("/run_now")
async def run_now():
    logging.info("Running scripts now...")
    run_scripts()
    return {"message": "Scripts executed"}

@app.get("/your_endpoint")
async def your_endpoint():
    return {"message": "Your API logic here"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("scheduler:app", host="0.0.0.0", port=5000)
