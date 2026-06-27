"""Temporary script to test database connectivity outside the Streamlit UI."""
import psycopg2

from data_loader import get_db_connection, get_db_url, load_lead_data


def mask_url(url: str | None) -> str:
    if not url:
        return "(not configured)"
    if "@" not in url:
        return url[:20] + "..."
    prefix, host_part = url.split("@", 1)
    user_part = prefix.rsplit(":", 1)[0]
    return f"{user_part}:***@{host_part}"


def main() -> None:
    print("=== Database connection test ===")
    db_url = get_db_url()
    print(f"DB_URL resolved: {mask_url(db_url)}")

    if not db_url:
        print("FAIL: No DB_URL found in secrets or environment")
        return

    print("\n--- Direct psycopg2.connect (bypasses Streamlit) ---")
    try:
        direct_conn = psycopg2.connect(db_url, connect_timeout=10)
        with direct_conn.cursor() as cur:
            cur.execute("SELECT 1 AS ok;")
            print(f"SELECT 1 result: {cur.fetchone()}")
        direct_conn.close()
        print("Direct connection: OK")
    except Exception as exc:
        print(f"Direct connection FAIL: {type(exc).__name__}: {exc}")

    print("\n--- get_db_connection() from data_loader ---")
    conn = get_db_connection()
    if conn is None:
        print("FAIL: get_db_connection() returned None")
        return

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 AS ok;")
            row = cur.fetchone()
        print(f"SELECT 1 result: {row}")
    except Exception as exc:
        print(f"FAIL: SELECT 1 raised {type(exc).__name__}: {exc}")
        return
    finally:
        conn.close()

    print("\n=== load_lead_data() test ===")
    try:
        df = load_lead_data()
        print(f"Rows returned: {len(df)}")
        if not df.empty:
            print(f"Columns: {list(df.columns)}")
    except Exception as exc:
        print(f"FAIL: load_lead_data() raised {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    main()
