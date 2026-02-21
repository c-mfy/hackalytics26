# BACKEND SERVER USING FASTAPI
# contains:
#   routes/endpoints
#   /: serves the frontend
#   /results: returns WER/transcription data as JSON
#   code to read CSV and compute data


from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Serve static files from the "static" folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve index.html at the root
@app.get("/")
async def home():
    return FileResponse("static/index.html")