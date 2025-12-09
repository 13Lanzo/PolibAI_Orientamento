import mysql.connector
from mysql.connector import errorcode

def crea_struttura_vuota():
    print("🐬 Connessione a XAMPP (MySQL) in corso...")

    # Configurazione Standard XAMPP
    config = {
        'user': 'root',
        'password': '',
        'host': 'localhost',
        'raise_on_warnings': True
    }

    try:
        # 1. Connessione al Server
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        # 2. Creazione Database (Vuoto)
        dbPoliba = 'poliba_chatbot'
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {dbPoliba} DEFAULT CHARACTER SET 'utf8'")
        print(f"✅ Database '{dbPoliba}' verificato/creato.")

        # 3. Selezione del DB
        conn.database = dbPoliba

        # 4. Creazione Tabella (Vuota)
        query_tabella = """
        CREATE TABLE IF NOT EXISTS mappe (
            id INT AUTO_INCREMENT PRIMARY KEY,
            chiave VARCHAR(100) NOT NULL UNIQUE,
            immagine_url TEXT NOT NULL,
            descrizione TEXT NOT NULL
        ) ENGINE=InnoDB
        """
        cursor.execute(query_tabella)
        print("✅ Tabella 'mappe' creata correttamente (senza dati).")

        conn.commit()
        cursor.close()
        conn.close()

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("❌ Errore: Username o Password di XAMPP sbagliati.")
        else:
            print(f"❌ Errore MySQL: {err}")
    else:
        print("🎉 Struttura completata! Il DB è pronto su XAMPP.")

if __name__ == '__main__':
    crea_struttura_vuota()