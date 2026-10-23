# Creazione dell'account e quindi iput utente
# - creazione della costante con tutti i campi che a noi interessano
UTENTI_CSV = "utenti_csv" 

CAMPO_REGISTRAZIONE = [

    "Username",
    "Password",
    "Conferma_Password",
    "Nome",
    "Cognome",
    "Nazione",
    "Citta",
    "Cap",
    "Telefono",
    "Email",
]


# - Creazione delle classi

class Utenti:

    def __init__(self, username, password, conferma_password, nome, cognome, nazione, citta, cap, telefono, email):
        self.username = self.validate_username (username)
        self.password = self.validate_password (password, conferma_password)
        self.conferma_password = self.validate_conferma_password (conferma_password, password)
        self.nome = nome.strip().title()
        self.cognome = cognome.strip().title()
        self.nazione = nazione.strip().title()
        self.citta = citta.strip().title()
        self.cap = cap.strip().title()
        self.telefono = telefono.strip()
        self.email = email.lower().strip()


#__________________________Pulizia__________________


    def validate_username(self, username):
        username_pulito = username.lower().strip()

        if len(username_pulito) < 5:
            raise ValueError("L'username deve contenere almeno 5 caratteri")
        return username_pulito

    def validate_password(self, password, conferma_password):
        password_pulita = password.strip()
        
        if len(password_pulita) < 6:
            raise ValueError("la password deve contenere: ")

        if not any(c.isupper() for c in password_pulita):
            raise ValueError("La password deve contenere almeno una lettera maiuscola.")

        if not any(c.isdigit() for c in password_pulita):
            raise ValueError("La password deve contenere almeno un numero.")    
        return password_pulita

    def validate_conferma_password(self, conferma_password, password):

        if conferma_password != self.password:
            raise ValueError("le password non sono uguali")
        return conferma_password
                             

    
        
        pass 


# Creazione di dati identificativi e quindi input utente

# Apro la funzione utenti_input per permettere all'utente di digitare i campi
def utenti_input():

    # apro il dictionary per trasportare i dati della lista chiamata all'inizio in questa funzione
    dati_utente = {}
   
    # Apro il ciclo per permettere al programma di rimanere qui dentro fino a che non finiamo le nostre operazioni
    # Con CAMPO_REGISTRAZIONE porto la lista
    for campo in CAMPO_REGISTRAZIONE:
       
        #creo una variabile e collego ad esso la lista per inserire il tutto
        dati_utente[campo.lower()] = input(f"Inserisci {campo}: ")
    
    #riporto i dati ottenuti allinterno della classe Utenti
    return Utenti(**dati_utente)


# - Creazione degli input e pulirli consecutivamente

# Creazione degli errori

# - Creazione validazione campi e messaggi di errore

# Creare file o leggerlo e poi salvarlo dopo verifica della chiave

# - Creazione e lettura file e salvataggio in database

# esci dalla pagina
pass

# esci dalla pagina
nuovo_utente = utenti_input()

# Stampiamo alcuni dati per verificare che la pulizia e l'inserimento abbiano funzionato
print("\n--- Utente Registrato Correttamente ---")
print(f"Username o email: {nuovo_utente.username}")
print(f"Nome: {nuovo_utente.nome}")
print(f"Email: {nuovo_utente.email}")