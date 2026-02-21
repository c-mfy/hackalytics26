# whisper_predict.py
from openai import OpenAI
from dotenv import load_dotenv
from jiwer import wer
import pandas as pd
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def transcribe_samples(csv_file: str, audio_dir: str, accents_to_test: list[str], sample_limit: int = 5):
    results = []
    try:
        df_metadata = pd.read_csv(csv_file)
    except FileNotFoundError:
        print("CSV file not found")
        return results

    for accent in accents_to_test:
        df_accent = df_metadata[df_metadata["accents"].str.contains(accent, na=False)].head(sample_limit)
        for _, row in df_accent.iterrows():
            filename = os.path.join(audio_dir, row["path"])
            ground_truth = str(row["sentence"]).lower().strip()

            if not os.path.exists(filename):
                print(f"File not found: {filename}")
                continue

            try:
                with open(filename, "rb") as audio_file:
                    transcription = client.audio.transcriptions.create(
                        model="gpt-4o-mini-transcribe",
                        file=audio_file
                    )
                predicted_text = transcription.text.lower().strip()
            except Exception as e:
                print(f"Error transcribing {filename}: {e}")
                predicted_text = ""

            error = wer(ground_truth, predicted_text)
            results.append({
                "accent": accent,
                "filename": row["path"],
                "ground_truth": ground_truth,
                "prediction": predicted_text,
                "wer": error
            })

    return results