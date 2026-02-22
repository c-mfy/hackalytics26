import pandas as pd
import re
import json
from collections import defaultdict
from jiwer import process_words

ACCENT_MAP = {
    "united states": "en",
    "american":      "en",
    "australian":    "au",
    "canadian":      "ce",
    "indian":        "in",
    "south africa": "sa",
}

ACCENT_NAMES = {
    "en": "General American",
    "au": "Australian English",
    "ce": "Canadian English",
    "in": "Indian English",
    "sa": "South African English",
}

def normalize_accent(raw):
    raw = str(raw).lower().strip()
    for key, code in ACCENT_MAP.items():
        if key in raw:
            return code
    return "other"

def clean(text):
    text = str(text).lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text

def run(
    transcripts_csv="data/simple_transcripts.csv",
    phoneme_csv="data/phoneme_counter.csv",
    summary_json="data/wer_summary.json",
    top_n_phonemes=5,
    top_n_words=5,
):
    df = pd.read_csv(transcripts_csv)
    df["accent_code"] = df["accents"].fillna("").apply(normalize_accent)
    df = df[df["accent_code"] != "other"].copy()

    summary = {}   # will be written to wer_summary.json

    # ── 1. OVERALL WER PER ACCENT ─────────────────────────────────────────────
    print("=" * 50)
    print("OVERALL WER PER ACCENT")
    print("=" * 50)
    for accent, group in df.groupby("accent_code"):
        valid = group[group["wer"].notna() & group["wer"].apply(lambda x: isinstance(x, float))]
        if valid.empty:
            print(f"WER for [{accent}]: no data")
            continue
        avg_wer = valid["wer"].mean() * 100  # stored as 0-1, convert to %
        print(f"WER for [{accent}]: {avg_wer:.2f}%")
        summary[accent] = {
            "wer": round(avg_wer, 2),
            "name": ACCENT_NAMES.get(accent, accent),
            "sample_count": len(valid),
        }

    # ── 2. TOP ERROR PHONEMES PER ACCENT ──────────────────────────────────────
    print()
    print("=" * 50)
    print("TOP PHONEMES BY ERROR RATE PER ACCENT")
    print("=" * 50)

    try:
        ph = pd.read_csv(phoneme_csv).set_index("phoneme")
        col_map = {"en": "en", "au": "au", "ce": "ce", "in": "in", "sa": "sa"}

        for accent in df["accent_code"].unique():
            ph_col  = col_map.get(accent)
            err_col = ph_col + "e" if ph_col else None

            if not ph_col or ph_col not in ph.columns or err_col not in ph.columns:
                print(f"\n[{accent}] phoneme data not available")
                continue

            sub = ph[[ph_col, err_col]].copy()
            sub = sub[sub[ph_col] > 0]
            sub["error_rate"] = sub[err_col] / sub[ph_col]
            top = sub.nlargest(top_n_phonemes, "error_rate")

            print(f"\n[{accent}] top {top_n_phonemes} phonemes by error rate:")
            top_phonemes = []
            for phoneme, row in top.iterrows():
                print(f"  {phoneme:<6} error rate: {row['error_rate']*100:.1f}%  ({int(row[err_col])}/{int(row[ph_col])})")
                top_phonemes.append({
                    "phoneme": phoneme,
                    "error_rate": round(row["error_rate"] * 100, 1),
                    "errors": int(row[err_col]),
                    "total": int(row[ph_col]),
                })

            if accent in summary:
                summary[accent]["top_phonemes"] = top_phonemes

    except FileNotFoundError:
        print("phoneme_counter.csv not found, skipping phoneme analysis")

    # ── 3. TOP ERROR WORDS PER ACCENT ─────────────────────────────────────────
    print()
    print("=" * 50)
    print(f"TOP {top_n_words} ERROR WORDS PER ACCENT")
    print("=" * 50)

    for accent, group in df.groupby("accent_code"):
        word_total  = defaultdict(int)
        word_errors = defaultdict(int)

        for _, row in group.iterrows():
            ref = clean(row["sentence"])
            hyp = clean(row["prediction"]) if pd.notna(row.get("prediction")) else ""
            if not ref:
                continue

            out = process_words(ref, hyp)
            for chunk in out.alignments[0]:
                if chunk.type not in ("equal", "substitute", "delete"):
                    continue
                ref_words = ref.split()[chunk.ref_start_idx : chunk.ref_end_idx]
                is_error  = chunk.type != "equal"
                for word in ref_words:
                    word_total[word]  += 1
                    if is_error:
                        word_errors[word] += 1

        candidates = {w: word_errors[w] / word_total[w]
                      for w in word_total if word_total[w] >= 2}

        if not candidates:
            print(f"\n[{accent}] not enough data for word analysis")
            continue

        top_words = sorted(candidates, key=candidates.get, reverse=True)[:top_n_words]
        print(f"\n[{accent}] top {top_n_words} words by error rate:")
        top_words_list = []
        for word in top_words:
            rate = candidates[word] * 100
            print(f"  '{word:<18} error rate: {rate:.1f}%  ({word_errors[word]}/{word_total[word]})")
            top_words_list.append({
                "word": word,
                "error_rate": round(rate, 1),
                "errors": word_errors[word],
                "total": word_total[word],
            })

        if accent in summary:
            summary[accent]["top_words"] = top_words_list

    # ── write summary JSON ────────────────────────────────────────────────────
    with open(summary_json, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nWER summary written to {summary_json}")

    return summary

if __name__ == "__main__":
    run()