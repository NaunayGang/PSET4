import os

import psycopg2

ROLES = [
    ("operator", "OPERATOR"),
    ("incident_commander", "INCIDENT_COMMANDER"),
    ("technical_responder", "TECHNICAL_RESPONDER"),
    ("manager", "MANAGER"),
    ("admin", "ADMIN"),
]

USERS = [
    ("operator1", "operator1@example.com", "OPERATOR"),
    ("commander1", "commander1@example.com", "INCIDENT_COMMANDER"),
    ("responder1", "responder1@example.com", "TECHNICAL_RESPONDER"),
    ("manager1", "manager1@example.com", "MANAGER"),
    ("admin1", "admin1@example.com", "ADMIN"),
]

PASSWORD_HASH = "disabled_for_testing_only"


def get_connection():
    db_url = os.getenv(
        "DATABASE_URL", "postgresql://incidentflow:incidentflow@db:5432/incidentflow"
    )
    return psycopg2.connect(db_url)


def seed_roles(conn):
    with conn.cursor() as cur:
        for username, role in ROLES:
            cur.execute(
                """
                INSERT INTO users (username, password_hash, role)
                VALUES (%s, %s, %s)
                ON CONFLICT (username) DO NOTHING
                """,
                (username, PASSWORD_HASH, role),
            )
    conn.commit()
    print(f"Seeded {len(ROLES)} roles")


def seed_test_users(conn):
    with conn.cursor() as cur:
        for username, email, role in USERS:
            cur.execute(
                """
                INSERT INTO users (username, password_hash, role)
                VALUES (%s, %s, %s)
                ON CONFLICT (username) DO NOTHING
                """,
                (username, PASSWORD_HASH, role),
            )
    conn.commit()
    print(f"Seeded {len(USERS)} test users")


def main():
    conn = get_connection()
    try:
        seed_roles(conn)
        seed_test_users(conn)
        print("Seeding completed successfully")
    finally:
        conn.close()


if __name__ == "__main__":
    main()

