import sqlite3

def main():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    print("Database created")

    user_table = """CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        user_id TEXT NOT NULL,
        username TEXT NOT NULL,
        test_score TEXT NOT NULL,
        state INTEGER NOT NULL, 
        task_number INTEGER NOT NULL,
        task_question INTEGER NOT NULL,
        test_var_tasks TEXT)"""

    c.execute(user_table)

    conn.commit()
    print("Table created")

    c.close()
    print("Cursor closed")
    conn.close()
    print("Database closed")

    input('Нажмите Enter для выхода\n')

if __name__ == '__main__':
    main()