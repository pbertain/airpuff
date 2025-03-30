import sys
import sqlite3


def get_atis_phone(db_name, icao):
    """
    Get the ATIS phone number for a given airport ICAO code.
    
    :param db_name: The name of the SQLite database file.
    :param icao: The ICAO code of the airport.
    :return: The formatted ATIS phone number or an error message if not found.
    """
    try:
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute("SELECT wx_phone FROM airports WHERE airport=?", (icao,))
        result = c.fetchone()
        conn.close()

        if result:
            wx_phone = result[0]
            atis_phone = f"tel://+1-{wx_phone}"
            return atis_phone
        else:
            return f"No phone number found for airport: {icao}"

    except sqlite3.Error as e:
        return f"Database error: {e}"


def main():
    """
    Main function to be executed when the script is run directly.
    """
    if len(sys.argv) != 2:
        print("Usage: python airport_info.py <ICAO>")
        return

    db_name = '/var/airpuff/data/airport_info.db'
    icao = sys.argv[1]
    print(get_atis_phone(db_name, icao))


if __name__ == "__main__":
    main()

