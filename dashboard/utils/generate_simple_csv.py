# converts original Mozilla transcript to a smaller one with only the needed information

import pandas as pd
from jiwer import wer
import os
from openai import OpenAI
from dotenv import load_dotenv
import re
from utils.fill_phonemes import update_phoneme_counts


ACCENT_MAP = {
    "united states": "en",
    "american": "en",
    "australian": "au",
    "canadian": "ce",
    "indian": "in",
    "south africa": "sa",
}

def normalize_accent(raw):
    raw = str(raw).lower().strip()
    for key, code in ACCENT_MAP.items():
        if key in raw:
            return code
    return None

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def normalize(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s]', '', text)  # remove punctuation
    text = re.sub(r'\s+', ' ', text)     # collapse multiple spaces
    return text

def create_simple_csv(input_csv="data/transcripts.tsv",
                      output_csv="data/simple_transcripts.csv",
                      audio_dir="data/cv_samples/",
                      accent_list=["en","au","ce","in","sa"]):

    full_dataframe = pd.read_csv(input_csv, sep='\t', low_memory=False)

    file_map = {}
    for accent in accent_list:
        accent_dir = audio_dir + accent
        if not os.path.exists(accent_dir):
            continue
        for f in os.listdir(accent_dir):
            file_map[f] = os.path.join(accent, f)

    full_dataframe["accent_code"] = full_dataframe["accents"].apply(normalize_accent)
    subset = full_dataframe[
        full_dataframe["accent_code"].isin(accent_list) &
        full_dataframe["path"].isin(file_map.keys())
    ].copy()
    subset['rel_path'] = subset['path'].map(file_map)

    # ── skip files already processed in the existing output CSV ──────────────
    already_done = set()
    if os.path.exists(output_csv):
        try:
            existing = pd.read_csv(output_csv)
            already_done = set(existing['path'].dropna().tolist())
            print(f"Found {len(already_done)} already-processed files, skipping them.")
        except Exception:
            pass

    subset = subset[~subset['path'].isin(already_done)].copy()

    if subset.empty:
        print("No new files to process.")
        update_phoneme_counts()
        return

    print(f"Processing {len(subset)} new file(s)...")

    # Add new columns
    subset['prediction'] = ''
    subset['wer'] = 0.0

    for idx, row in subset.iterrows():
        filename = os.path.join(audio_dir, row['rel_path'])
        ground_truth = row['sentence']
        error_sum = 0.0
        predicted_text = ""

        # transcribe 5 times and average the WER
        for _ in range(5):
            with open(filename, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    model="gpt-4o-mini-transcribe",
                    file=audio_file
                )
                predicted_text = transcription.text.lower().strip()
                error_sum += wer(normalize(ground_truth), normalize(predicted_text))

        subset.loc[idx, 'prediction'] = predicted_text
        avg_error = error_sum / 5
        subset.loc[idx, 'wer'] = avg_error
        print(f"Average WER: {avg_error:.4f} ({row['path']})")

    # ── append to existing CSV or create new one ──────────────────────────────
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    if os.path.exists(output_csv):
        combined = pd.concat([pd.read_csv(output_csv), subset], ignore_index=True)
        combined.to_csv(output_csv, index=False)
        print(f"Appended {len(subset)} new rows to {output_csv} ({len(combined)} total)")
    else:
        subset.to_csv(output_csv, index=False)
        print(f"Created {output_csv} with {len(subset)} rows")

    update_phoneme_counts()