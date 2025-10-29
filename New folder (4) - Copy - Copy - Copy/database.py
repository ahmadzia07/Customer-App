import psycopg2
from psycopg2.extras import RealDictCursor
from config import Config
import logging


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:



    def __init__(self):
        self.config = Config()
        self.connection = None
        
        
    def connect(self):
        """Establish connection to PostgreSQL database"""
        try:
            self.connection = psycopg2.connect(
                host=self.config.DB_HOST,
                port=self.config.DB_PORT,
                database=self.config.DB_NAME,
                user=self.config.DB_USER,
                password=self.config.DB_PASSWORD
            )
            logger.info("Successfully connected to PostgreSQL database")
            return self.connection
        except psycopg2.Error as e:
            logger.error(f"Error connecting to database: {e}")
            raise
            

    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
            
    def get_cursor(self):
        """Get database cursor with RealDictCursor for easier JSON conversion"""
        if not self.connection:
            self.connect()
        return self.connection.cursor(cursor_factory=RealDictCursor)

    def get_table_columns(self, table_name: str):
        """Return a set of column names for given table (lowercased)."""
        query = (
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema = 'public' AND table_name = %s"
        )
        rows = self.execute_query(query, (table_name,), fetch=True)
        return {row['column_name'].lower() for row in rows}
        
    def execute_query(self, query, params=None, fetch=True):
        """Execute a database query and return results.

        - SELECT queries return a list of rows (dicts)
        - INSERT/UPDATE/DELETE without RETURNING return affected rowcount
        - Any statement with RETURNING returns a list of rows
        """
        #any
        try:
            cursor = self.get_cursor()
            cursor.execute(query, params)

            upper_query = query.strip().upper()

            if fetch:
                if upper_query.startswith('SELECT') or ' RETURNING ' in upper_query:
                    result = cursor.fetchall()
                    self.connection.commit()
                    return result
                # Non-select and no RETURNING: return rowcount
                self.connection.commit()
                return cursor.rowcount
            else:
                self.connection.commit()
                return cursor.rowcount

        except psycopg2.Error as e:
            logger.error(f"Database query error: {e}")
            self.connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()

def init_database():
    """Ensure DB is reachable without altering existing schemas.

    We only open and close a connection here to validate credentials.
    This avoids creating tables/triggers that may not match the user's schema.
    """
    db = Database()
    try:
        db.connect()
        logger.info("Database connection validated")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise
    finally:
        db.disconnect()

# Global database instance
db_instance = Database()
