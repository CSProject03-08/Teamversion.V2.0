import sqlite3
import pandas as pd

DB_PATH = "db/users.db"

def connect():
    return sqlite3.connect(DB_PATH)

def get_user_trips(user_id: int) -> pd.DataFrame:
    """
    Returns all trips assigned to a given user (employee)
    using the user_trips mapping table.
    """

    conn = connect()

    query = """
        SELECT 
            t.trip_ID,
            t.destination,
            t.start_date,
            t.end_date,
            t.occasion
        FROM trips t
        JOIN user_trips ut ON t.trip_ID = ut.trip_ID
        WHERE ut.user_ID = ?
        ORDER BY t.start_date ASC
    """

    df = pd.read_sql_query(query, conn, params=(user_id,))
    conn.close()
    return df
