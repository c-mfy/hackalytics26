# BACKEND SERVER USING FASTAPI
# contains:
#   routes/endpoints
#   /: serves the frontend
#   /results: returns WER/transcription data as JSON
#   code to read CSV and compute data


from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import pandas as pd
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os

# utils imports
# from utils.whisper_output import transcribe_samples
from utils.generate_simple_csv import create_simple_csv

create_simple_csv()

app = FastAPI()

AUDIO_DIR = "./data/cv_samples/en-au"
CSV_FILE = "./data/simple_transcripts.csv"
SAMPLE_LIMIT = 5

class EvaluationRequest(BaseModel):
    accents: list[str]

# Serve static files from the "static" folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# Endpoint index.html at the root
@app.get("/")
async def home():
    return FileResponse("static/index.html")

# Endpoint to get WER results
@app.get("/results")
async def getResults():
    try:
        dataframe = pd.read_csv("data/simple_transcripts.csv") # path to csv
        data = dataframe.to_dict(orient="records") # convert to list of dicts
        return JSONResponse(content=data)
    except FileNotFoundError:
        return JSONResponse(content={"error": "simple_transcripts.csv not found"}, status_code = 404)
    
@app.post("/evaluate")
def evaluate_accents(req: EvaluationRequest):
    results = transcribe_samples(CSV_FILE, AUDIO_DIR, req.accents, SAMPLE_LIMIT)

    if not results:
        return JSONResponse(content={"error": "No results, check CSV or audio files"}, status_code=404)

    df_results = pd.DataFrame(results)
    summary = df_results.groupby("accent")["wer"].mean().to_dict()

    return {
        "summary": summary,
        "results": results
    }

@app.get("/research")                       
async def research():
    return FileResponse("static/research.html")
