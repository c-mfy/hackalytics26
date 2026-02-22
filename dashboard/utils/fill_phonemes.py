import pandas as pd
import pronouncing
import re
from jiwer import process_words

#lowercase, remove puncatuation, collapse spaces
def clean(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text

#map full accent string to abbreiviations in phoneme counter
ACCENT_MAP = {
    "american english": "en",
    "united states english": "en",
    "australian english": "au",
    "canadian english": "ce",
    "indian english": "in",
    "south africa": "sa",
}

#convert "Australian English" to "au"
def normalize_accent(raw):
    raw = raw.lower().strip()
    for key, code in ACCENT_MAP.items():
        if key in raw:
            return code
    return "other"

def update_phoneme_counts(
        transcripts_csv="data/simple_transcripts.csv",
        phoneme_csv="data/phoneme_counter.csv"
):
    # Load CSVs
    df_trans = pd.read_csv(transcripts_csv)
    df_phoneme = pd.read_csv(phoneme_csv).set_index("phoneme")

    # reset all counts to 0 before recomputing
    accent_cols = ["en","ene","au","aue","ce","cee","in","ine","sa","sae"]
    df_phoneme[accent_cols] = 0

    df_trans["accent_code"] = df_trans["accents"].fillna("").apply(normalize_accent)

    #loop through transciption sample
    for _, row in df_trans.iterrows():
        accent = row["accent_code"]
        if accent == "other":
            continue

        total_col = accent        # ex. "au" total times appeared for australian
        error_col = accent + "e"  # ex. "aue" errors for this phoneme

        ref = clean(str(row["sentence"]))
        hyp = clean(str(row["prediction"]))

        #skip if string is empty
        if not ref or not hyp:
            continue

        #align reference vs hypothesis & return their labels (equal, subsitute, insert, delete)
        out = process_words(ref, hyp)

        for chunk in out.alignments[0]:
            #ignore insertions
            if chunk.type not in ("equal", "substitute", "delete"):
                continue

            #get reference words
            ref_words = ref.split()[chunk.ref_start_idx : chunk.ref_end_idx]
            #chunk not equal means word was wrong
            is_error  = chunk.type != "equal"

            for word in ref_words:
                #loop up reference words pronounciation in dictionary
                phones = pronouncing.phones_for_word(word)
                #skip if not in CMU dictionary
                if not phones:
                    continue
                #split each hypothesis word into phonemes
                for p in phones[0].split():
                    # strip stress digits
                    p = re.sub(r"\d", "", p)  
                    #if phoneme not in row, skip
                    if p not in df_phoneme.index:
                        continue
                    df_phoneme.loc[p, total_col] += 1
                    #if word was wrong, increment error
                    if is_error:
                        df_phoneme.loc[p, error_col] += 1

    #save updated counts to csv
    df_phoneme.reset_index().to_csv(phoneme_csv, index=False)
    print("Done — phoneme_counter.csv updated")
