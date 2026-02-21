# converts original Mozilla transcript to a smaller one with only the needed information

import pandas as pd
from jiwer import wer
import os
from openai import OpenAI
from dotenv import load_dotenv
import re

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def create_simple_csv(input_csv="data/transcripts.csv",
                      output_csv="data/simple_transcripts.csv",
                      audio_dir = "data/cv_samples/en-au",
                      accents=["Australian English"],
                      samples_per_accent=5):
    full_dataframe = pd.read_csv(input_csv) # C:\Users\Xinyu Su\Documents\GitHub\hackalytics26\dashboard\data\cv_samples\en-au\common_voice_en_618602.mp3
    simplified_rows = []

    selected_files = os.listdir(audio_dir)
    # print(selected_files)

    subset = full_dataframe[full_dataframe['path'].isin(selected_files)].copy()
    # print(f"SIMPLIFIED: {subset}")

    # Add new columns
    subset['prediction'] = 'some_value'
    subset['wer'] = 0.0


    for idx, row in subset.iterrows():
        filename = audio_dir + "/" + row['path']

        with open(filename, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                    model="gpt-4o-mini-transcribe",
                    file=audio_file
                )
            predicted_text = transcription.text.lower().strip()
            subset.loc[idx, 'prediction'] = predicted_text

            # compute WER
            ground_truth = row['sentence']
            # print(f"Ground truth: {ground_truth}")
            # print(repr(ground_truth))
            # print(repr(predicted_text))

            def normalize(text):
                text = text.lower().strip()
                text = re.sub(r'[^\w\s]', '', text)  # remove punctuation
                text = re.sub(r'\s+', ' ', text)     # collapse multiple spaces
                return text

            error = wer(normalize(ground_truth), normalize(predicted_text))
            # error = wer(ground_truth, predicted_text)
            # print(error)
            subset.loc[idx, 'wer'] = error
            
    
    """
    for accent in accents:
        accent_dataframe = full_dataframe[
            full_dataframe['accents'].str.contains(accent, case=False, na=False)
        ].head(samples_per_accent)
        print(accent_dataframe)

        for _, row in accent_dataframe.iterrows():
            filename = audio_dir + "common_voice_en_618602.mp3"
            # filename = os.path.normpath(os.path.join(audio_dir, row["path"]))
            print(os.listdir("data/cv_samples/en-au")[:5])  # what's actually there
            print(accent_dataframe["path"].head())                            # what the CSV references
            if not os.path.exists(filename):
                print(f"File not found: {filename}")
                continue

            ground_truth = str(row["sentence"]).lower().strip()
            print(f"Ground truth: {ground_truth}")

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
    """
    
    # simplified_dataframe = pd.DataFrame(simplified_rows)
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    subset.to_csv(output_csv, index=False)
    print(f"Simplified CSV saved to {output_csv}")