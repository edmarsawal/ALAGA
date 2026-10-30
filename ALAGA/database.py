
import mysql.connector
from mysql.connector import Error
import hashlib
import secrets
import hmac

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "123456789!", 
    "database": "alaga_db"
}

def get_connection():
    """Connect to the ALAGA MySQL database."""
    return mysql.connector.connect(**DB_CONFIG)

def hash_password(password):
    """Hash a password using PBKDF2 and a random salt."""
    salt = secrets.token_bytes(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        600_000
    )

    return f"{salt.hex()}${password_hash.hex()}"


def verify_password(password, stored_hash):
    """Verify a password against its stored hash."""
    try:
        salt_hex, hash_hex = stored_hash.split("$", 1)
        salt = bytes.fromhex(salt_hex)

        calculated_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            600_000
        )

        return hmac.compare_digest(
            calculated_hash.hex(),
            hash_hex
        )

    except (ValueError, TypeError, AttributeError):
        return False

def get_columns(cursor, table_name):
    """Get existing column names from a table."""
    cursor.execute(f"SHOW COLUMNS FROM `{table_name}`")
    return {row[0] for row in cursor.fetchall()}


def add_column_if_missing(
    cursor, table_name, column_name, definition
):
    """Add a column only if it does not already exist."""
    columns = get_columns(cursor, table_name)

    if column_name not in columns:
        cursor.execute(
            f"ALTER TABLE `{table_name}` "
            f"ADD COLUMN `{column_name}` {definition}"
        )
        print(f"Added column: {table_name}.{column_name}")

def create_tables(cursor):

    # USERS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            full_name VARCHAR(100) NOT NULL,
            role VARCHAR(50) NOT NULL DEFAULT 'User',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ANIMALS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS animals (
            animal_id INT AUTO_INCREMENT PRIMARY KEY,
            tag_number VARCHAR(50) NOT NULL UNIQUE,
            animal_name VARCHAR(100) NOT NULL,
            species VARCHAR(50) NOT NULL,
            breed VARCHAR(100),
            sex VARCHAR(20),
            birth_date DATE,
            weight DECIMAL(10,2),
            status VARCHAR(30) DEFAULT 'Active',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # VACCINATIONS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vaccinations (
            vaccination_id INT AUTO_INCREMENT PRIMARY KEY,
            animal_id INT NOT NULL,
            vaccine_name VARCHAR(100) NOT NULL,
            vaccination_date DATE NOT NULL,
            next_due_date DATE,
            veterinarian VARCHAR(100),
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (animal_id)
                REFERENCES animals(animal_id)
                ON DELETE CASCADE
        )
    """)

    # FEEDING RECORDS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feeding_records (
            feeding_id INT AUTO_INCREMENT PRIMARY KEY,
            animal_id INT NOT NULL,
            feed_type VARCHAR(100) NOT NULL,
            quantity DECIMAL(10,2) NOT NULL,
            unit VARCHAR(30) NOT NULL DEFAULT 'kg',
            feeding_date DATE NOT NULL,
            feeding_time TIME NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (animal_id)
                REFERENCES animals(animal_id)
                ON DELETE CASCADE
        )
    """)

    # HEALTH RECORDS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS health_records (
            health_id INT AUTO_INCREMENT PRIMARY KEY,
            animal_id INT NOT NULL,
            record_date DATE NOT NULL,
            condition_name VARCHAR(150) NOT NULL,
            treatment TEXT,
            veterinarian VARCHAR(100),
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (animal_id)
                REFERENCES animals(animal_id)
                ON DELETE CASCADE
        )
    """)

    # BREEDING RECORDS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS breeding_records (
            breeding_id INT AUTO_INCREMENT PRIMARY KEY,
            animal_id INT NOT NULL,
            mate_tag_number VARCHAR(50),
            breeding_date DATE NOT NULL,
            expected_birth_date DATE,
            actual_birth_date DATE,
            offspring_count INT NOT NULL DEFAULT 0,
            status VARCHAR(50) DEFAULT 'Pending',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (animal_id)
                REFERENCES animals(animal_id)
                ON DELETE CASCADE
        )
    """)

def migrate_existing_tables(cursor):

    # ANIMALS
    animal_columns = get_columns(cursor, "animals")

    if "tag_number" not in animal_columns:
        cursor.execute("""
            ALTER TABLE animals
            ADD COLUMN tag_number VARCHAR(50) NULL
        """)

        if "animal_tag" in animal_columns:
            cursor.execute("""
                UPDATE animals
                SET tag_number = animal_tag
                WHERE tag_number IS NULL
                  AND animal_tag IS NOT NULL
            """)

        print("Added column: animals.tag_number")

    # FEEDING RECORDS
    add_column_if_missing(
        cursor,
        "feeding_records",
        "unit",
        "VARCHAR(30) NOT NULL DEFAULT 'kg'"
    )

    add_column_if_missing(
        cursor,
        "feeding_records",
        "feeding_time",
        "TIME NULL"
    )

    # BREEDING RECORDS
    add_column_if_missing(
        cursor,
        "breeding_records",
        "mate_tag_number",
        "VARCHAR(50) NULL"
    )

    add_column_if_missing(
        cursor,
        "breeding_records",
        "actual_birth_date",
        "DATE NULL"
    )

    add_column_if_missing(
        cursor,
        "breeding_records",
        "offspring_count",
        "INT NOT NULL DEFAULT 0"
    )

def initialize_database():
    """Create tables, migrate columns, and create the admin account."""
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        create_tables(cursor)
        migrate_existing_tables(cursor)

        cursor.execute(
            "SELECT id FROM users WHERE username = %s",
            ("admin",)
        )

        admin_exists = cursor.fetchone()

        if admin_exists is None:
            cursor.execute("""
                INSERT INTO users
                    (username, password_hash, full_name, role)
                VALUES (%s, %s, %s, %s)
            """, (
                "admin",
                hash_password("Admin123!"),
                "Administrator",
                "System Administrator"
            ))

            print("Default administrator created.")
            print("Username: admin")
            print("Password: Admin123!")

        connection.commit()
        print("ALAGA database initialized successfully!")

    except Error as error:
        if connection is not None and connection.is_connected():
            connection.rollback()

        print("Database initialization failed:", error)
        raise

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


def authenticate_user(username, password):
    """Return user details if login succeeds; otherwise None."""
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, username, password_hash, full_name, role
            FROM users
            WHERE username = %s
        """, (username.strip(),))

        user = cursor.fetchone()

        if user and verify_password(
            password, user["password_hash"]
        ):
            return {
                "id": user["id"],
                "username": user["username"],
                "full_name": user["full_name"],
                "role": user["role"]
            }

        return None

    except Error as error:
        print("Login database error:", error)
        return None

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()

if __name__ == "__main__":
    try:
        initialize_database()

        connection = get_connection()
        print("MySQL connection successful!")
        connection.close()

    except Error as error:
        print("Unable to connect to MySQL.")
        print("Check the DB_CONFIG settings.")
        print("Error:", error)
