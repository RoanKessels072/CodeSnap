from database.db import init_db
if __name__ == '__main__':
    print("Initializing database...")
    init_db()
    print("Done! Check pgAdmin to see your tables.")