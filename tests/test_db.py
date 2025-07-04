from app.db import SessionLocal

def test_database_connection():
    """
    Verifies that a connection to the PostgreSQL database can be established.
    Executes a trivial SELECT statement to confirm connectivity.
    """
    try:
        db = SessionLocal()
        result = db.execute("SELECT 1").scalar()
        assert result == 1
    finally:
        db.close()