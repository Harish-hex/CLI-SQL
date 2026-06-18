import sqlite3

def connect_db():
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()

    return conn, cursor

def run_query(cursor, conn, querry):
    cursor.execute(querry)
    conn.commit()

def print_results(cursor):
    rows = cursor.fetchall()
    for i in rows:
        print(i)

def main():
    conn, cursor = connect_db()
    while True:
        query = input("sql> ")
        if query == ".exit":
            break

        try:
            run_query(cursor,conn,query)
            if query.lower().startswith("select"):
                print_results(cursor)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()

