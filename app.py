import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from logger import logger  # Import the logger


app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#test new branch 

from routes import router as AMLRouter

app.include_router(AMLRouter, tags=["AmlCFT"], prefix="/amlcft")

if __name__ == "__main__":
    logger.info("Starting the application...")
    #uvicorn.run(app, host="0.0.0.0", port=8000)
    uvicorn.run(
    app, 
    host="0.0.0.0", 
    port=8000,  
    timeout_keep_alive=120  # Set Keep-Alive timeout to 120 seconds
    )
