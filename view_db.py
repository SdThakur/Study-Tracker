"""Interactive terminal viewer for study_tracker.db"""
import sqlite3
import sys

def view():
    db_file = "study_tracker.db"
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        tables = [r[0] for r in cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()]
        if not tables:
            print("No tables found in database.")
            return

        print(f"\n{'='*60}")
        print(f"DATABASE: {db_file}")
        print(f"{'='*60}")

        for table in tables:
            cursor.execute(f"PRAGMA table_info('{table}')")
            columns = [col[1] for col in cursor.fetchall()]
            
            cursor.execute(f"SELECT * FROM '{table}'")
            rows = cursor.fetchall()

            print(f"\n[TABLE: {table.upper()}] ({len(rows)} rows)")
            print("-" * 60)
            print(" | ".join(f"{col:<15}" for col in columns))
            print("-" * 60)
            if not rows:
                print("  (empty table)")
            for row in rows:
                formatted_row = []
                for val in row:
                    val_str = str(val)
                    if len(val_str) > 20 and "$argon2" in val_str:
                        val_str = "[argon2_hash]"
                    elif len(val_str) > 25:
                        val_str = val_str[:22] + "..."
                    formatted_row.append(f"{val_str:<15}")
                print(" | ".join(formatted_row))
        print(f"\n{'='*60}\n")
        conn.close()
    except Exception as e:
        print(f"Error reading database: {e}")

if __name__ == "__main__":
    view()
