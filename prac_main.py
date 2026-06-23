import sqlite3
from openai import OpenAI
import logging
from dotenv import load_dotenv
import os
import tabulate
import time

load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENAPI_KEY")
)

logging.basicConfig(
    filename="sql_runner.log",
    level=logging.INFO,
    format="%(asctime)s | %(message)s"
)
logging.info("===SESSION STARTED===")

def connect_db():
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()

    return conn, cursor

def run_query(cursor, conn, querry):
    logging.info(
        f"QUERY | {querry}"
    )
    start = time.perf_counter()
    cursor.execute(querry)
    conn.commit()
    end = time.perf_counter()
    return (end - start) * 1000 # Return the execution time in milliseconds
    

def print_results(cursor,time_taken):
    rows = cursor.fetchall()
    headers = [description[0] for description in cursor.description]
    print(tabulate.tabulate(rows, headers=headers, tablefmt="grid"))
    print(f"Execution successful. Time Taken: {time_taken:.2f} ms")

def get_llm_hint(query,error):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "user",
                "content":
                f"""Query:{query} Error:{error} (CONTEXT: THIS IS A SQLite BASED QUERRY RUNNER. GIVE ANSWER BASED ON SQLite QUERRIES.) Give me a simple,oneline hint to fix the error. Dont give me the full querry, just a hint to fix the error. or pinpoint whats casuing the error and what should be changes for the querry to work. Dont give me the full querry, just a hint to fix the error. or pinpoint whats casuing the error and what should be changes for the querry to work."""
            }
        ]
    )
    return response.choices[0].message.content


def ask_llm(question):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "user",
                "content":
                f"""(CONTEXT: THIS IS A SQLite BASED QUERRY RUNNER. GIVE ANSWER BASED ON SQLite QUERRIES.) Question:{question} Give me a simple,oneline answer to the question. dont give me a long answer in anyway. **IMPORTANT** ONLY ANSWER THE QUESTION IF ITS RELATED TO SQL, if its not related to SQL, just say "I can only answer SQL related questions"."""
            }
        ]
    )
    return response.choices[0].message.content

def main():
    conn, cursor = connect_db()
    while True:
        query = input("sql> ")
        if query == ".exit":
            print("Goodbye!")
            logging.info("===SESSION ENDED===")
            break
        elif query == ".ask":
            question = input("ask your question: ")
            answer = ask_llm(question)
            logging.info(
                f"ASK | {question} | {answer}"
            )
            print(f"Answer: {answer}")
            continue

        try:
            time_taken = run_query(cursor,conn,query)
            if query.lower().startswith("select"):
                print_results(cursor,time_taken)
            else:
                print(f"Execution successful. Time Taken: {time_taken:.2f} ms")

        except Exception as e:
            print(f"Error: {e}")
            hint = get_llm_hint(query,e)
            print(f"Hint: {hint}")
            logging.error(
                f"ERROR & HINT| {e} | {hint}"
            )

if __name__ == "__main__":
    main()
