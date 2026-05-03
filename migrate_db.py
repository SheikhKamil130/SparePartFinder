"""
Database Migration Script: SQLite to PostgreSQL
This script helps migrate data from SQLite to PostgreSQL database.
"""
import sqlite3
import psycopg2
from psycopg2.extras import execute_values
import os
from dotenv import load_dotenv

load_dotenv()

def export_sqlite_data():
    """Export data from SQLite database"""
    sqlite_db = 'instance/spareparts.db'
    
    if not os.path.exists(sqlite_db):
        print(f"SQLite database not found: {sqlite_db}")
        return None
    
    conn = sqlite3.connect(sqlite_db)
    cursor = conn.cursor()
    
    # Export Parts table
    cursor.execute("SELECT * FROM part")
    parts = cursor.fetchall()
    part_columns = [description[0] for description in cursor.description]
    
    # Export PriceRecord table
    cursor.execute("SELECT * FROM price_record")
    price_records = cursor.fetchall()
    price_columns = [description[0] for description in cursor.description]
    
    conn.close()
    
    print(f"Exported {len(parts)} parts from SQLite")
    print(f"Exported {len(price_records)} price records from SQLite")
    
    return {
        'parts': {'data': parts, 'columns': part_columns},
        'price_records': {'data': price_records, 'columns': price_columns}
    }

def import_to_postgres(data):
    """Import data to PostgreSQL database"""
    if not data:
        print("No data to import")
        return
    
    # Get PostgreSQL connection string
    db_url = os.environ.get('DATABASE_URL', '')
    if not db_url or not db_url.startswith('postgresql://'):
        print("PostgreSQL DATABASE_URL not configured in .env")
        return
    
    # Parse connection string
    # Format: postgresql://user:password@host:port/database
    try:
        conn_info = db_url.replace('postgresql://', '')
        user_pass, rest = conn_info.split('@')
        user, password = user_pass.split(':')
        host_port_db = rest.split('/')
        host_port = host_port_db[0]
        database = host_port_db[1] if len(host_port_db) > 1 else 'spareparts'
        
        if ':' in host_port:
            host, port = host_port.split(':')
        else:
            host = host_port
            port = '5432'
        
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        cursor = conn.cursor()
        
        # Create tables if they don't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS part (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL,
                description TEXT,
                category VARCHAR(50),
                price FLOAT,
                quantity INTEGER DEFAULT 0,
                in_stock BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_record (
                id SERIAL PRIMARY KEY,
                part_name VARCHAR(100) NOT NULL,
                retailer VARCHAR(100) NOT NULL,
                price FLOAT NOT NULL,
                availability VARCHAR(100),
                url VARCHAR(500),
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        
        # Import Parts
        if data['parts']['data']:
            insert_parts = """
                INSERT INTO part (id, name, description, category, price, quantity, in_stock, created_at)
                VALUES %s
                ON CONFLICT (id) DO NOTHING
            """
            execute_values(cursor, insert_parts, data['parts']['data'])
            print(f"Imported {len(data['parts']['data'])} parts to PostgreSQL")
        
        # Import Price Records
        if data['price_records']['data']:
            insert_prices = """
                INSERT INTO price_record (id, part_name, retailer, price, availability, url, scraped_at)
                VALUES %s
                ON CONFLICT (id) DO NOTHING
            """
            execute_values(cursor, insert_prices, data['price_records']['data'])
            print(f"Imported {len(data['price_records']['data'])} price records to PostgreSQL")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✓ Migration completed successfully!")
        
    except Exception as e:
        print(f"Error during PostgreSQL import: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("="*60)
    print("SQLite to PostgreSQL Migration Tool")
    print("="*60)
    
    # Step 1: Export from SQLite
    print("\n1. Exporting data from SQLite...")
    data = export_sqlite_data()
    
    if not data:
        print("Migration aborted - no data to migrate")
        return
    
    # Step 2: Confirm migration
    print("\n2. Ready to import to PostgreSQL")
    confirm = input("Continue with migration? (yes/no): ")
    
    if confirm.lower() != 'yes':
        print("Migration cancelled")
        return
    
    # Step 3: Import to PostgreSQL
    print("\n3. Importing data to PostgreSQL...")
    import_to_postgres(data)
    
    print("\n" + "="*60)
    print("Migration process completed!")
    print("="*60)
    print("\nNext steps:")
    print("1. Update .env file: USE_POSTGRES=true")
    print("2. Restart your Flask application")
    print("3. Verify data integrity")

if __name__ == "__main__":
    main()
