import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.tokenize import sent_tokenize

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
    df = pd.read_sql_query(query, conn)
    return df


def summarize_with_tfidf(text, top_n=5):
    sentences = sent_tokenize(text)
    if len(sentences) <= top_n:
        return text  # Not enough to summarize

    # TF-IDF Vectorization
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(sentences)
    scores = tfidf_matrix.sum(axis=1).A1  # Sum TF-IDF scores per sentence

    # Rank and select top N sentences
    ranked_sentences = sorted(
        ((score, sent) for score, sent in zip(scores, sentences)),
        reverse=True
    )
    summary = " ".join([sent for _, sent in ranked_sentences[:top_n]])
    return summary


def generate_wordcloud_from_summary(summary, filename):
    if not summary.strip():
        print(f"Warning: No summary text for {filename}. Skipping.")
        return
    wc = WordCloud(width=800, height=400, background_color='white').generate(summary)

    plt.figure(figsize=(12, 6))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.title("Word Cloud of Summarized Open-ended Responses")
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()
    print(f"Word cloud saved: {filename}")


def main():
    conn = sqlite3.connect(DB_FILE)
    df_open = load_open_ended_responses(conn)
    conn.close()

    # Merge all open-ended text into one document
    full_text = " ".join(df_open['open_ended_text'].dropna().astype(str).values)
    summary = summarize_with_tfidf(full_text, top_n=5)

    # Save summary (optional)
    # with open(os.path.join("data", "summary.txt"), "w", encoding="utf-8") as f:
    #     f.write(summary)

    # Generate word cloud from summary
    generate_wordcloud_from_summary(summary, os.path.join(PLOT_DIR, "wordcloud_summary.png"))


if __name__ == "__main__":
    main()
