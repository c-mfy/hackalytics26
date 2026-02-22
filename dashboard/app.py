# BACKEND SERVER USING FASTAPI
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import pandas as pd
import os, io, json, math, shutil

from utils.generate_simple_csv import create_simple_csv, normalize_accent
from utils.calculate import run as run_calculate

app = FastAPI()

AUDIO_DIR = "./data/cv_samples/"
CSV_FILE  = "./data/simple_transcripts.csv"

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def home():
    return FileResponse("static/index.html")

@app.get("/research")
async def research():
    return FileResponse("static/research.html")

# ── GET /results ──────────────────────────────────────────────────────────────
@app.get("/results")
async def getResults():
    try:
        dataframe = pd.read_csv(CSV_FILE)
        data = dataframe.to_dict(orient="records")
        clean = json.loads(
            json.dumps(data, default=lambda x: None if (isinstance(x, float) and not math.isfinite(x)) else x)
        )
        return JSONResponse(content=clean)
    except FileNotFoundError:
        return JSONResponse(content={"error": "simple_transcripts.csv not found"}, status_code=404)

# ── GET /wer-summary ──────────────────────────────────────────────────────────
# Returns pre-computed per-accent WER, top phonemes, top words from calculate.py
@app.get("/wer-summary")
async def werSummary():
    summary_path = "data/wer_summary.json"
    # regenerate if missing or CSV is newer than summary
    needs_regen = not os.path.exists(summary_path)
    if not needs_regen and os.path.exists(CSV_FILE):
        needs_regen = os.path.getmtime(CSV_FILE) > os.path.getmtime(summary_path)

    if needs_regen:
        try:
            run_calculate()
        except Exception as e:
            return JSONResponse(content={"error": f"calculate failed: {str(e)}"}, status_code=500)

    try:
        with open(summary_path) as f:
            return JSONResponse(content=json.load(f))
    except FileNotFoundError:
        return JSONResponse(content={"error": "wer_summary.json not found"}, status_code=404)

# ── POST /upload ──────────────────────────────────────────────────────────────
@app.post("/upload")
async def upload(
    tsv_file:    UploadFile = File(...),
    audio_files: list[UploadFile] = File(...)
):
    try:
        # 1. save TSV
        os.makedirs("data", exist_ok=True)
        tsv_path  = "data/transcripts.tsv"
        tsv_bytes = await tsv_file.read()
        with open(tsv_path, "wb") as f:
            f.write(tsv_bytes)

        # 2. map filenames → accent codes from TSV
        df_tsv = pd.read_csv(io.BytesIO(tsv_bytes), sep="\t", low_memory=False)
        df_tsv["accent_code"] = df_tsv["accents"].fillna("").apply(normalize_accent)
        path_to_accent = dict(zip(df_tsv["path"], df_tsv["accent_code"]))

        # 3. sort audio files into accent subfolders
        saved, skipped = 0, 0
        for audio in audio_files:
            filename = os.path.basename(audio.filename)
            accent   = path_to_accent.get(filename)
            if not accent or accent == "other":
                skipped += 1
                continue
            dest_dir = os.path.join(AUDIO_DIR, accent)
            os.makedirs(dest_dir, exist_ok=True)
            with open(os.path.join(dest_dir, filename), "wb") as f:
                f.write(await audio.read())
            saved += 1

        if saved == 0:
            return JSONResponse(
                content={"error": "No audio files matched accent codes in the TSV."},
                status_code=400
            )

        # 4. transcribe + compute WER (appends to existing CSV)
        create_simple_csv(input_csv=tsv_path, output_csv=CSV_FILE, audio_dir=AUDIO_DIR)

        # 5. recompute summary JSON so /wer-summary is up to date
        run_calculate()

        return JSONResponse(content={
            "status": "ok",
            "audio_saved": saved,
            "audio_skipped": skipped,
            "message": f"Processed {saved} audio files."
        })

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)