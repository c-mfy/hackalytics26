# converts original Mozilla transcript to a smaller one with only the needed information

import pandas as pd
from jiwer import wer
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def create_simple_csv(input_csv="data/transcripts.csv",
                      output_csv="data/simple_transcripts.csv",
                      audio_dir = "./data/cv_samples/en-au",
                      accents=["Australian English"],
                      samples_per_accent=10):
    full_dataframe = pd.read_csv(input_csv)
    simplified_rows = []

    for accent in accents:
        accent_dataframe = full_dataframe[
            full_dataframe['accents'].str.contains(accent, case=False, na=False)
        ].head(samples_per_accent)

        for _, row in accent_dataframe.iterrows():
            filename = os.path.join(audio_dir, row["path"])
            if not os.path.exists(filename):
                print(f"⚠️ File not found: {filename}")
                continue

            ground_truth = str(row["sentence"]).lower().strip()

            # Transcribe audio with Whisper
            with open(filename, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    model="gpt-4o-mini-transcribe",
                    file=audio_file
                )
            predicted_text = transcription.text.lower().strip()

            # Compute WER
            error = wer(ground_truth, predicted_text)

            simplified_rows.append({
                "filename": row["path"],
                "accent": accent,
                "ground_truth": ground_truth,
                "prediction": predicted_text,
                "wer": error
            })

            print(f"[{accent}] {row['path']} WER={error:.2f}")
    
    simplified_dataframe = pd.DataFrame(simplified_rows)
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    simplified_dataframe.to_csv(output_csv, index=False)
    print(f"Simplified CSV saved to {output_csv}")