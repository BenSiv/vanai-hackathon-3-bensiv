import sqlite3

DB_FILE = "data/ai_survey.db"

def test_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # 1. List all questions with answer option counts
    print("Questions with counts of answer options:")
    cur.execute("""
    SELECT q.question_code, q.question_text, COUNT(ao.answer_option_id) AS option_count
    FROM Questions q
    LEFT JOIN AnswerOptions ao ON q.question_id = ao.question_id
    GROUP BY q.question_id
    ORDER BY q.question_code
    """)
    for row in cur.fetchall():
        print(f"{row[0]}: {row[1]} (Options: {row[2]})")
    print("-" * 80)

    # 2. Count total responses per question
    print("Response counts per question:")
    cur.execute("""
    SELECT q.question_code, q.question_text, COUNT(r.response_id) AS response_count
    FROM Questions q
    LEFT JOIN Responses r ON q.question_id = r.question_id
    GROUP BY q.question_id
    ORDER BY response_count DESC
    """)
    for row in cur.fetchall():
        print(f"{row[0]}: {row[1]} — Responses: {row[2]}")
    print("-" * 80)

    # 3. Show distribution of answers for a specific question, e.g. Q1
    question_code = "Q1"
    print(f"Answer distribution for question {question_code}:")
    cur.execute("""
    SELECT ao.option_text, COUNT(r.response_id) AS frequency
    FROM Responses r
    JOIN AnswerOptions ao ON r.answer_option_id = ao.answer_option_id
    JOIN Questions q ON ao.question_id = q.question_id
    WHERE q.question_code = ?
    GROUP BY ao.option_text
    ORDER BY frequency DESC
    """, (question_code,))
    for row in cur.fetchall():
        print(f"{row[0]}: {row[1]}")
    print("-" * 80)

    # 4. Show count of open-ended responses for a question, e.g. Q10
    question_code_open = "Q10"
    print(f"Count of open-ended responses for question {question_code_open}:")
    cur.execute("""
    SELECT COUNT(*) FROM Responses r
    JOIN Questions q ON r.question_id = q.question_id
    WHERE q.question_code = ?
      AND r.open_ended_text IS NOT NULL
      AND TRIM(r.open_ended_text) != ''
    """, (question_code_open,))
    count = cur.fetchone()[0]
    print(f"Open-ended responses: {count}")
    print("-" * 80)

    # 5. Show some sample open-ended responses for Q10
    print(f"Sample open-ended responses for question {question_code_open}:")
    cur.execute("""
    SELECT r.open_ended_text FROM Responses r
    JOIN Questions q ON r.question_id = q.question_id
    WHERE q.question_code = ?
      AND r.open_ended_text IS NOT NULL
      AND TRIM(r.open_ended_text) != ''
    LIMIT 5
    """, (question_code_open,))
    rows = cur.fetchall()
    if rows:
        for i, row in enumerate(rows, 1):
            print(f"{i}. {row[0]}")
    else:
        print("No open-ended responses found.")
    print("-" * 80)

    # === New part: Show distribution and open-ended count for Q12 ===

    question_code_q12 = "Q12"
    print(f"Answer distribution for question {question_code_q12}:")
    cur.execute("""
    SELECT ao.option_text, COUNT(r.response_id) AS frequency
    FROM Responses r
    JOIN AnswerOptions ao ON r.answer_option_id = ao.answer_option_id
    JOIN Questions q ON ao.question_id = q.question_id
    WHERE q.question_code = ?
    GROUP BY ao.option_text
    ORDER BY frequency DESC
    """, (question_code_q12,))
    rows = cur.fetchall()
    if rows:
        for row in rows:
            print(f"{row[0]}: {row[1]}")
    else:
        print("No answer option responses found.")
    print("-" * 80)

    print(f"Count of open-ended responses for question {question_code_q12}:")
    cur.execute("""
    SELECT COUNT(*) FROM Responses r
    JOIN Questions q ON r.question_id = q.question_id
    WHERE q.question_code = ?
      AND r.open_ended_text IS NOT NULL
      AND TRIM(r.open_ended_text) != ''
    """, (question_code_q12,))
    count = cur.fetchone()[0]
    print(f"Open-ended responses: {count}")
    print("-" * 80)

    print(f"Sample open-ended responses for question {question_code_q12}:")
    cur.execute("""
    SELECT r.open_ended_text FROM Responses r
    JOIN Questions q ON r.question_id = q.question_id
    WHERE q.question_code = ?
      AND r.open_ended_text IS NOT NULL
      AND TRIM(r.open_ended_text) != ''
    LIMIT 5
    """, (question_code_q12,))
    rows = cur.fetchall()
    if rows:
        for i, row in enumerate(rows, 1):
            print(f"{i}. {row[0]}")
    else:
        print("No open-ended responses found.")
    print("-" * 80)

    conn.close()

if __name__ == "__main__":
    test_db()
