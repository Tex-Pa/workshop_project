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
        self.username = username.lower().strip()
        self.password = password
        self.conferma_password = conferma_password
        self.nome = nome.strip().title()
        self.cognome = cognome.strip().title()
        self.nazione = nazione.strip().title()
        self.citta = citta.strip().title()
        self.cap = cap.strip().title()
        self.telefono = telefono.strip()
        self.email = email.lower().strip()
        
        pass 


# Creazione di dati identificativi e quindi input utente

# - Creazione degli input e pulirli consecutivamente

# Creazione degli errori

# - Creazione validazione campi e messaggi di errore

# Creare file o leggerlo e poi salvarlo dopo verifica della chiave

# - Creazione e lettura file e salvataggio in database

# esci dalla pagina
