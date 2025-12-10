import mysql.connector
from mysql.connector import errorcode

def popola_database():
    print("Connessione a XAMPP (MySQL) per inserimento dati...")

    # Configurazione Standard XAMPP
    config = {
        'user': 'root',
        'password': '',
        'host': 'localhost',
        'database': 'poliba_chatbot', # Ci colleghiamo direttamente al DB esistente
        'raise_on_warnings': False    # Evita blocchi se ci sono avvisi non critici
    }

    try:
        # 1. Connessione al Server MySQL
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        print(f"Connesso al database 'poliba_chatbot'.")

        # 2. Creazione Tabella (Solo se non esiste, per sicurezza)
        query_tabella = """
        CREATE TABLE IF NOT EXISTS mappe (
            id INT AUTO_INCREMENT PRIMARY KEY,
            chiave VARCHAR(100) NOT NULL UNIQUE,
            immagine_url TEXT NOT NULL,
            descrizione TEXT NOT NULL
        ) ENGINE=InnoDB
        """
        cursor.execute(query_tabella)
        print("Tabella 'mappe' verificata.")

        # 3. DATI DA INSERIRE
        # I percorsi corrispondono alla tua cartella: src/assets/images/maps/
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
            ),
            (
                "immagine_campus_LabDDV_ulpiani",
                "assets/images/maps/immagine_campus_LabDDV_ulpiani.jpg",
                "Entrando dall'ingresso in via Celso Ulpiani, proseguendo dritto troverai subito dinnanzi a te le aule Celso Ulpiani (del dipartimento DArCoD). Entrando nell'edificio, troverai quasi subito l'aula G4, ovvero il laboratorio di Elettronica della prof.ssa De Venuto!"
            ),
            (
                "immagine_campus_LabDDV_reDavid",
                "assets/images/maps/immagine_campus_LabDDV_reDavid.jpg",
                "Entrando dall'ingresso in via Re David, prosegui sempre dritto, scendendo da una rampa e proseguendo sempre dritto fino al dipartimento di Architettura. A questo punto svolta a sinistra e prosegui fin quando non vedrai dinnanzi a te le aule Celso Ulpiani (del dipartimento DArCoD). Entrando nell'edificio, troverai quasi subito l'aula G4, ovvero il laboratorio di Elettronica della prof.ssa De Venuto!"
            ),
            (
                "immagine_campus_LabDDV_Orabona2",
                "assets/images/maps/immagine_campus_LabDDV_Orabona2.jpg",
                "Percorso consigliato: entrando dallingresso per soli pedoni in via Orabona, svolta a destra e prosegui dritto. A questo punto potrai seguire il percorso dell'ingresso principale di via Orabona. Quindi prosegui sempre dritto per circa 200 metri e camminando lungo la strada asfaltata che divide gli edifici del Politecnico e il dipartimento di Geologia, vedrai sulla tua sinistra le aule Celso Ulpiani (del dipartimento DArCoD). Entrando nell'edificio, troverai quasi subito l'aula G4, ovvero il laboratorio di Elettronica della prof.ssa De Venuto!"
            ),
            (
                "immagine_campus_LabDDV_Orabona1",
                "assets/images/maps/immagine_campus_LabDDV_Orabona1.jpg",
                "Entrando dall'ingresso principale di via Orabona, prosegui sempre dritto per circa 200 metri e camminando lungo la strada asfaltata che divide gli edifici del Politecnico e il dipartimento di Geologia, vedrai sulla tua sinistra le aule Celso Ulpiani (del dipartimento DArCoD). Entrando nell'edificio, troverai quasi subito l'aula G4, ovvero il laboratorio di Elettronica della prof.ssa De Venuto!"
            )
        ]

        # 4. Esecuzione Inserimento/Aggiornamento
        query_insert = """
        INSERT INTO mappe (chiave, immagine_url, descrizione) 
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            immagine_url=VALUES(immagine_url), 
            descrizione=VALUES(descrizione)
        """
        
        cursor.executemany(query_insert, dati_mappe)
        conn.commit() 

        print(f"Successo! Inseriti/Aggiornati {cursor.rowcount} percorsi nel database.")

        cursor.close()
        conn.close()

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Errore: Username o Password di XAMPP sbagliati.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Errore: Il database 'poliba_chatbot' non esiste.")
        else:
            print(f"Errore MySQL: {err}")

if __name__ == '__main__':
    popola_database()
