import psycopg
from psycopg.rows import dict_row
from config import DB_CONFIG

def get_connection():
    """Get database connection"""
    return psycopg.connect(
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        dbname=DB_CONFIG['database'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password']
    )

def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    """Execute a query and optionally fetch results"""
    conn = get_connection()
    cursor = conn.cursor(row_factory=dict_row)
    
    try:
        cursor.execute(query, params)
        
        if fetch_one:
            result = cursor.fetchone()
        elif fetch_all:
            result = cursor.fetchall()
        else:
            result = None
            
        conn.commit()
        return result
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def execute_insert(query, params=None):
    """Execute insert and return the inserted id using RETURNING"""
    conn = get_connection()
    cursor = conn.cursor(row_factory=dict_row)
    
    try:
        cursor.execute(query + " RETURNING id", params)
        result = cursor.fetchone()
        conn.commit()
        return result['id'] if result else None
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()
