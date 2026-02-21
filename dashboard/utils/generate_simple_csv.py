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
                      accent_list=["ae","au","ca","in","sa"]):
    
    full_dataframe = pd.read_csv(input_csv) # C:\Users\Xinyu Su\Documents\GitHub\hackalytics26\dashboard\data\cv_samples\en-au\common_voice_en_618602.mp3

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

            # compute WER FIVE times and compute average WER
            count = 5
            current_error = 0.0
            error_sum = 0.0
            error = 0.0
            while count > 0:

                ground_truth = row['sentence']
                # print(f"Ground truth: {ground_truth}")
                # print(repr(ground_truth))
                # print(repr(predicted_text))

                def normalize(text):
                    text = text.lower().strip()
                    text = re.sub(r'[^\w\s]', '', text)  # remove punctuation
                    text = re.sub(r'\s+', ' ', text)     # collapse multiple spaces
                    return text

                current_error = wer(normalize(ground_truth), normalize(predicted_text))
                # error = wer(ground_truth, predicted_text)
                # print(error)
                error_sum += current_error
                count -= 1

            # TODO: count total phonemes and update phoneme_counter.csv ['total'] HERE
            # [total list of phonemes detected], [list of erroneous phonemes] = phoneme_analysis()
            # for each phoneme in total phoneme list, phoneme_counter.csv row['total'] += 1
            # also if accent = ae, au, ce, in, sa, phoneme_counter.csv row[accent] += 1

            # TODO: count missed phonemes and update phoneme_counter.csv ['error'] HERE
            # for each erroneous phoneme in total erroneous list, phoneme_counter.csv row['error'] += 1


            error = error_sum / 5
            print(f"Average WER: {error} = {error_sum} / 5")

            subset.loc[idx, 'wer'] = error

    # simplified_dataframe = pd.DataFrame(simplified_rows)
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    subset.to_csv(output_csv, index=False)
    print(f"Simplified CSV saved to {output_csv}")