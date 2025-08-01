import sqlite3
import pandas as pd
import re
import math
import logging

QUESTIONS_MD = "data/questions.md"
ANSWERS_CSV = "data/answers.csv"
DB_FILE = "data/ai_survey.db"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler("data/build_db.log")
    ]
)

def parse_questions_md(filepath):
    questions = {}
    current_q = None
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if line.startswith("## Q"):
            current_q = line[3:].strip()  # e.g. "Q1"
            questions[current_q] = {"text": "", "type": "", "options": []}
            logging.info(f"Found question block: {current_q}")
        elif current_q:
            if line.startswith("question:"):
                questions[current_q]["text"] = line[len("question:"):].strip()
            elif line.startswith("type:"):
                questions[current_q]["type"] = line[len("type:"):].strip()
            elif line.startswith("- "):
                option = line[2:].strip()
                questions[current_q]["options"].append(option)
    logging.info(f"Parsed {len(questions)} questions from markdown.")
    return questions

def main():
    logging.info("Connecting to SQLite database...")
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    logging.info("Creating tables...")
    cur.executescript("""
    DROP TABLE IF EXISTS Respondents;
    DROP TABLE IF EXISTS Questions;
    DROP TABLE IF EXISTS AnswerOptions;
    DROP TABLE IF EXISTS Responses;

    CREATE TABLE Questions (
        question_id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_code TEXT UNIQUE,
        question_text TEXT,
        question_type TEXT
    );

    CREATE TABLE AnswerOptions (
        answer_option_id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_id INTEGER,
        option_text TEXT,
        option_code TEXT,
        is_other BOOLEAN DEFAULT 0,
        FOREIGN KEY (question_id) REFERENCES Questions(question_id)
    );

    CREATE TABLE Responses (
        response_id INTEGER PRIMARY KEY AUTOINCREMENT,
        respondent_id TEXT,
        question_id INTEGER,
        answer_option_id INTEGER,
        open_ended_text TEXT,
        FOREIGN KEY (question_id) REFERENCES Questions(question_id),
        FOREIGN KEY (answer_option_id) REFERENCES AnswerOptions(answer_option_id)
    );
    """)

    questions = parse_questions_md(QUESTIONS_MD)

    question_code_to_id = {}
    option_lookup = {}

    logging.info("Inserting questions and answer options into database...")
    for q_code, q in questions.items():
        cur.execute(
            "INSERT INTO Questions (question_code, question_text, question_type) VALUES (?, ?, ?)",
            (q_code, q["text"], q["type"])
        )
        qid = cur.lastrowid
        question_code_to_id[q_code] = qid

        if q["options"]:
            logging.info(f"Inserting {len(q['options'])} options for question {q_code}...")
        for opt in q["options"]:
            is_other = 1 if "other" in opt.lower() else 0
            cur.execute(
                "INSERT INTO AnswerOptions (question_id, option_text, option_code, is_other) VALUES (?, ?, ?, ?)",
                (qid, opt, opt, is_other)
            )
            aid = cur.lastrowid
            option_lookup[(q_code, opt)] = aid

    conn.commit()
    logging.info("Questions and options inserted.")

    logging.info("Loading responses CSV...")
    df = pd.read_csv(ANSWERS_CSV)
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].fillna("")

    logging.info(f"Processing {len(df)} respondents' answers...")

    inserted_count = 0
    skipped_count = 0
    batch_size = 500

    for idx, row in df.iterrows():
        respondent_id = str(idx)

        for col in df.columns:
            m = re.match(r"(Q\d+)(_OE)?(_.*)?", col)
            if not m:
                continue

            q_code = m.group(1)
            is_open_end_col = bool(m.group(2))
            suffix = m.group(3) or ""

            if q_code not in question_code_to_id:
                continue

            qid = question_code_to_id[q_code]
            q_type = questions[q_code]["type"]
            val = str(row[col]).strip()

            if val == "":
                skipped_count += 1
                continue

            if q_type == "multi_choice":
                if val.lower() in ["1", "true", "checked", "yes"]:
                    matched_aid = None
                    suffix_key = suffix.lstrip("_").lower()
                    for opt_text in questions[q_code]["options"]:
                        if suffix_key and suffix_key in opt_text.lower():
                            matched_aid = option_lookup.get((q_code, opt_text))
                            if matched_aid:
                                break
                    if not matched_aid and val in [opt for opt in questions[q_code]["options"]]:
                        matched_aid = option_lookup.get((q_code, val))
                    if matched_aid:
                        cur.execute(
                            "INSERT INTO Responses (respondent_id, question_id, answer_option_id) VALUES (?, ?, ?)",
                            (respondent_id, qid, matched_aid)
                        )
                        inserted_count += 1
            elif q_type == "single_choice":
                aid = option_lookup.get((q_code, val))
                if aid:
                    cur.execute(
                        "INSERT INTO Responses (respondent_id, question_id, answer_option_id) VALUES (?, ?, ?)",
                        (respondent_id, qid, aid)
                    )
                    inserted_count += 1
            elif q_type == "open_end" or is_open_end_col:
                if val != "" and not (isinstance(val, float) and math.isnan(val)) and val.lower() != "nan":
                    text_to_insert = val
                else:
                    text_to_insert = None

                cur.execute(
                    "INSERT INTO Responses (respondent_id, question_id, open_ended_text) VALUES (?, ?, ?)",
                    (respondent_id, qid, text_to_insert)
                )
                inserted_count += 1

        if (idx + 1) % batch_size == 0:
            conn.commit()
            logging.info(f"Processed {idx + 1} respondents so far...")

    conn.commit()
    logging.info(f"Finished processing. Inserted {inserted_count} responses, skipped {skipped_count} empty values.")
    conn.close()

    logging.info(f"SQLite database '{DB_FILE}' has been created and populated.")

if __name__ == "__main__":
    main()
