import mysql.connector
from mysql.connector import errorcode

def popola_database():
    print("🐬 Connessione a XAMPP (MySQL) per inserimento dati...")

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

        # 2. Selezione Database (Creazione se non esiste)
        dbPoliba = 'poliba_chatbot'
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {dbPoliba} DEFAULT CHARACTER SET 'utf8'")
        conn.database = dbPoliba

        # 3. Creazione Tabella (Se non esiste)
        query_tabella = """
        CREATE TABLE IF NOT EXISTS mappe (
            id INT AUTO_INCREMENT PRIMARY KEY,
            chiave VARCHAR(100) NOT NULL UNIQUE,
            immagine_url TEXT NOT NULL,
            descrizione TEXT NOT NULL
        ) ENGINE=InnoDB
        """
        cursor.execute(query_tabella)
        print("✅ Tabella 'mappe' verificata.")

        # 4. DATI DA INSERIRE (Popolamento)
        # Nota: I percorsi puntano alla cartella che hai creato tu: assets/images/maps/
        dati_mappe = [
            (
                "mappa_campus_poliLibrary_Orabona", 
                "assets/images/maps/mappa_campus_poliLibrary_Orabona.png", 
                "Partendo dall'ingresso per soli pedoni di via Orabona, prosegui dritto fino a quando non vedrai sulla tua sinistra un ufficio vetrato e delle porte scorrevoli. A questo punto entra dentro l'edificio e prendendo l'ascensore, giungi al terzo piano. Sarai arrivato alla poliLibrary!"
            ),
            (
                "mappa_campus_poliLibrary_reDavid", 
                "assets/images/maps/mappa_campus_poliLibrary_reDavid.png", 
                "Entrato dall'ingresso di via Re David, gira leggermente a destra e prosegui dritto fino a un ufficio vetrato con la scritta POLIBA CONTROL. A questo punto entra in questo edificio, attraverso le porte scorrevoli e prendi l'ascensore, giungi al terzo piano. Sarai arrivato alla poliLibrary!"
            ),
            (
                "mappa_campus_poliLibrary", 
                "assets/images/maps/mappa_campus_poliLibrary.png", 
                "Ecco a te una mappa del campus di Poliba, con la poliLibrary in evidenza!"
            ),
            (
                "ufficio_mongiello_Orabona1",
                "assets/images/maps/ufficio_mongiello_Orabona1.png",
                "Entrando dall'ingresso principale del campus, in via Orabona, prosegui dritto fino a quando non vedrai delle scale sulla tua sinistra e sali fino al primo piano. Sulla tua destra vedrai l'AULA MAGNA ATTILIO ALTO. Prosegui dritto fino a quando non vedrai una piccola porta in fondo, affianco all'aula magna. Entrando in questo edificio, giungi fino al terzo piano e sarai arrivato all'ufficio della prof.ssa Mongiello!"
            ),
            (
                "ufficio_mongiello_Orabona2",
                "assets/images/maps/ufficio_mongiello_Orabona2.png",
                "Entrando dall'ingresso per soli pedoni in via Orabona, prosegui dritto fin quando sulla tua destra non vedrai un grande spazio centrale (Atrio Cherubini); a questo punto attraverso e sali con delle scale grandi al primo piano, dove di fronte a te vedrai L'AULA MAGNA ATTILIO ALTO. Prosegui sulla sinistra fino a quando non vedrai una piccola porta in fondo, affianco all'aula magna. Entrando in questo edificio, giungi fino al terzo piano e sarai arrivato all'ufficio della prof.ssa Mongiello!"
            ),
            (
                "ufficio_mongiello_reDavid",
                "assets/images/maps/ufficio_mongiello_reDavid.png",
                "Entrato dall'ingresso di via Re David, gira leggermente a destra e prosegui dritto fino a quando dinnanzi a te vedrai un grande spazio centrale (Atrio Cherubini); a questo punto attraverso e sali con delle scale grandi al primo piano, dove di fronte a te vedrai L'AULA MAGNA ATTILIO ALTO. Prosegui sulla sinistra fino a quando non vedrai una piccola porta in fondo, affianco all'aula magna. Entrando in questo edificio, giungi fino al terzo piano e sarai arrivato all'ufficio della prof.ssa Mongiello!"
            )

            # Puoi aggiungere qui altri percorsi se hai caricato altre immagini
        ]

        # 5. Esecuzione Inserimento
        # Usiamo "ON DUPLICATE KEY UPDATE" per aggiornare i dati se esistono già senza dare errore
        query_insert = """
        INSERT INTO mappe (chiave, immagine_url, descrizione) 
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            immagine_url=VALUES(immagine_url), 
            descrizione=VALUES(descrizione)
        """
        
        cursor.executemany(query_insert, dati_mappe)
        conn.commit() # IMPORTANTE: Salva le modifiche!

        print(f"🎉 Successo! Inseriti/Aggiornati {cursor.rowcount} percorsi nel database.")

        cursor.close()
        conn.close()

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("❌ Errore: Username o Password di XAMPP sbagliati.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("❌ Errore: Il database non esiste.")
        else:
            print(f"❌ Errore MySQL: {err}")

if __name__ == '__main__':
    popola_database()