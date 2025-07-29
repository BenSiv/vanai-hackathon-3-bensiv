import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud

DB_FILE = "data/ai_survey.db"
PLOT_DIR = "plot"

os.makedirs(PLOT_DIR, exist_ok=True)

def load_open_ended_responses(conn):
    query = """
    SELECT r.respondent_id, q.question_code, q.question_text, r.open_ended_text
    FROM Responses r
    JOIN Questions q ON r.question_id = q.question_id
    WHERE r.open_ended_text IS NOT NULL AND r.open_ended_text <> ''
    """
    return pd.read_sql_query(query, conn)

def generate_wordcloud(open_ended_series, filename="open_ended_wordcloud.png"):
    text = " ".join(open_ended_series.dropna().astype(str).values).strip()
    if not text:
        print(f"Warning: No text found for word cloud: {filename}. Skipping.")
        return
    wc = WordCloud(width=800, height=400, background_color='white').generate(text)

    plt.figure(figsize=(12, 6))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.title("Word Cloud of All Open-ended Responses")
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()
    print(f"Word cloud saved: {filename}")

def main():
    conn = sqlite3.connect(DB_FILE)
    df_open = load_open_ended_responses(conn)

    # Generate word cloud from all open-ended text
    generate_wordcloud(df_open['open_ended_text'], os.path.join(PLOT_DIR, "wordcloud_all_open_ended.png"))

    conn.close()

if __name__ == "__main__":
    main()
