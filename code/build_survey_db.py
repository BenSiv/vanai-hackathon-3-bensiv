import sqlite3
import pandas as pd
import re
import math

QUESTIONS_MD = "data/questions.md"
ANSWERS_CSV = "data/answers.csv"
DB_FILE = "data/ai_survey.db"

def parse_questions_md(filepath):
    questions = {}
    current_q = None
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if line.startswith("## Q"):
            # New question block start
            current_q = line[3:].strip()  # e.g. "Q1"
            questions[current_q] = {"text": "", "type": "", "options": []}
        elif current_q:
            if line.startswith("question:"):
                questions[current_q]["text"] = line[len("question:"):].strip()
            elif line.startswith("type:"):
                questions[current_q]["type"] = line[len("type:"):].strip()
            elif line.startswith("- "):
                option = line[2:].strip()
                questions[current_q]["options"].append(option)
    return questions

def main():
    # Connect and create tables
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
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

    # Parse questions.md
    questions = parse_questions_md(QUESTIONS_MD)

    question_code_to_id = {}
    option_lookup = {}

    # Insert Questions and AnswerOptions
    for q_code, q in questions.items():
        cur.execute(
            "INSERT INTO Questions (question_code, question_text, question_type) VALUES (?, ?, ?)",
            (q_code, q["text"], q["type"])
        )
        qid = cur.lastrowid
        question_code_to_id[q_code] = qid
        for opt in q["options"]:
            is_other = 1 if "other" in opt.lower() else 0
            # Use option text as option_code for simplicity
            cur.execute(
                "INSERT INTO AnswerOptions (question_id, option_text, option_code, is_other) VALUES (?, ?, ?, ?)",
                (qid, opt, opt, is_other)
            )
            aid = cur.lastrowid
            option_lookup[(q_code, opt)] = aid

    conn.commit()

    # Load answers.csv
    df = pd.read_csv(ANSWERS_CSV)
    # Fill NaN only in object columns, avoiding dtype warnings
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].fillna("")

    # Use DataFrame index as respondent_id (string)
    for idx, row in df.iterrows():
        respondent_id = str(idx)

        for col in df.columns:
            # Expect columns like Q1, Q1_OE, Q5_1, Q5_Healthcare, etc.
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
                continue

            if q_type == "multi_choice":
                # Multi-choice columns might be:
                # - one per option (like Q5_Healthcare)
                # - values: 1, true, checked, yes etc. mean selected
                if val.lower() in ["1", "true", "checked", "yes"]:
                    matched_aid = None
                    suffix_key = suffix.lstrip("_").lower()
                    for opt_text in questions[q_code]["options"]:
                        if suffix_key and suffix_key in opt_text.lower():
                            matched_aid = option_lookup.get((q_code, opt_text))
                            if matched_aid:
                                break
                    # fallback: if suffix doesn't match, try matching full val as option text
                    if not matched_aid and val in [opt for opt in questions[q_code]["options"]]:
                        matched_aid = option_lookup.get((q_code, val))
                    if matched_aid:
                        cur.execute(
                            "INSERT INTO Responses (respondent_id, question_id, answer_option_id) VALUES (?, ?, ?)",
                            (respondent_id, qid, matched_aid)
                        )
            elif q_type == "single_choice":
                aid = option_lookup.get((q_code, val))
                if aid:
                    cur.execute(
                        "INSERT INTO Responses (respondent_id, question_id, answer_option_id) VALUES (?, ?, ?)",
                        (respondent_id, qid, aid)
                    )
            elif q_type == "open_end" or is_open_end_col:
                if val != "" and not (isinstance(val, float) and math.isnan(val)) and val.lower() != "nan":
                    text_to_insert = val
                else:
                    text_to_insert = None

                cur.execute(
                    "INSERT INTO Responses (respondent_id, question_id, open_ended_text) VALUES (?, ?, ?)",
                    (respondent_id, qid, text_to_insert)
                )

    conn.commit()
    conn.close()

    print(f"SQLite database '{DB_FILE}' has been created and populated.")

if __name__ == "__main__":
    main()
