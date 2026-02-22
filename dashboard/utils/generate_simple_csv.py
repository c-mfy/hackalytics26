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
    "south african": "sa",
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
                      audio_dir = "data/cv_samples/",
                      accent_list=["en","au","ce","in","sa"]):
    
    full_dataframe = pd.read_csv(input_csv, sep='\t') # C:\Users\Xinyu Su\Documents\GitHub\hackalytics26\dashboard\data\cv_samples\en-au\common_voice_en_618602.mp3

    file_map = {}
    for accent in accent_list:
        for f in os.listdir(audio_dir + accent):
            file_map[f] = os.path.join(accent, f)
    print(list(file_map.values()))

    full_dataframe["accent_code"] = full_dataframe["accents"].apply(normalize_accent)
    subset = full_dataframe[
        full_dataframe["accent_code"].isin(accent_list) &
        full_dataframe["path"].isin(file_map.keys())
    ].copy()
    # print(f"SIMPLIFIED: {subset}")
    subset['rel_path'] = subset['path'].map(file_map)
    # Add new columns
    subset['prediction'] = 'some_value'
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

        # save last prediction as a sample and average WER
        subset.loc[idx, 'prediction'] = predicted_text
        avg_error = error_sum / 5
        subset.loc[idx, 'wer'] = avg_error
        print(f"Average WER: {avg_error} = {error_sum} / 5")

            # TODO: count total phonemes and update phoneme_counter.csv ['total'] HERE
            # [total list of phonemes detected], [list of erroneous phonemes] = phoneme_analysis()
            # for each phoneme in total phoneme list, phoneme_counter.csv row['total'] += 1
            # also if accent = ae, au, ce, in, sa, phoneme_counter.csv row[accent] += 1

            # TODO: count missed phonemes and update phoneme_counter.csv ['error'] HERE
            # for each erroneous phoneme in total erroneous list, phoneme_counter.csv row['error'] += 1

    # simplified_dataframe = pd.DataFrame(simplified_rows)
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    subset.to_csv(output_csv, index=False)
    print(f"Simplified CSV saved to {output_csv}")
    update_phoneme_counts()