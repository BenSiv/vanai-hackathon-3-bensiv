import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import subprocess
from tqdm.auto import tqdm

DB_FILE = "data/ai_survey.db"
PLOT_DIR = "plot"
MODEL = "llama3.2"  # Your local Ollama model

os.makedirs(PLOT_DIR, exist_ok=True)

def load_open_ended_responses(conn):
    query = """
    SELECT question_code, question_text, open_ended_text
    FROM Responses
    JOIN Questions USING(question_id)
    WHERE open_ended_text IS NOT NULL AND open_ended_text <> ''
    """
    return pd.read_sql_query(query, conn)

def summarize_with_ollama(prompt, model=MODEL):
    try:
        result = subprocess.run(
            ["ollama", "run", model],
            input=prompt,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            timeout=120
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"[Error] Ollama summarization failed: {e}")
        return ""

def generate_wordcloud(text, filename):
    if not text.strip():
        print(f"[Skipped] Empty summary for: {filename}")
        return
    wc = WordCloud(width=1000, height=500, background_color="white").generate(text)
    plt.figure(figsize=(12, 6))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()
    print(f"[Saved] {filename}")

def main():
    conn = sqlite3.connect(DB_FILE)
    df = load_open_ended_responses(conn)

    grouped = df.groupby("question_code")
    print(f"[Info] Processing {len(grouped)} open-ended question(s)...")

    for q_code, group in tqdm(grouped, desc="Questions", unit="question"):
        all_text = "\n".join(group["open_ended_text"].astype(str).values)
        question_text = group["question_text"].iloc[0]
        print(f"\nSummarizing {q_code}: {question_text[:60]}...")

        prompt = (
            f"Summarize the key themes from the following open-ended survey responses "
            f"to the question: \"{question_text}\"\n\n"
            f"{all_text}\n\n"
            "Return a concise summary suitable for visualizing in a word cloud."
        )
        summary = summarize_with_ollama(prompt)

        if summary:
            out_path = os.path.join(PLOT_DIR, f"wordcloud_summary_{q_code}.png")
            generate_wordcloud(summary, out_path)
        else:
            print(f"[Warning] No summary returned for {q_code}")

    conn.close()
    print("\nAll word clouds generated.")

if __name__ == "__main__":
    main()
