# Analisi del Progetto

**progetto**: Sistema di machine learning per l’automatizzazione dell’accesso a una struttura privata  
**componenti gruppo:**  Manuel Sannicolò, Isabel Zoner  
**materia**: Autonomia Informatica  
**data inizio progetto**: 16/09/2025

# ---

Indice 

1. [Introduzione](#1-introduzione)  
2. [Obiettivi e scopo](#2-obiettivi-e-scopo)  
3. [Contesto e ambito](#3-contesto-e-ambito)  
4. [Requisiti funzionali](#4-requisiti-funzionali)  
5. [Requisiti non funzionali](#5-requisiti-non-funzionali)  
6. [Rischi e criticità](#6-analisi-dei-rischi-e-criticità)  
7. [Diagramma caso d’uso](#7-diagramma-caso-d’uso) 

---

# 1\. Introduzione 

Il progetto riguarda lo sviluppo di un sistema di machine learning in grado di rilevare, riconoscere e leggere targhe tramite una fotocamera, con l’obiettivo di rendere automatico l’ingresso all'interno di una struttura ai soli utenti autorizzati. Più in particolare, il sistema è stato progettato per la gestione dell’entrata in una struttura scolastica, in modo tale da consentire l’accesso soltanto a insegnanti, responsabili scolastici e studenti che utilizzano veicoli a due ruote, come motocicli o biciclette. 

Il funzionamento del nostro sistema è basato su tecniche di computer vision, OCR e tracking. Questo perché permettono di rilevare il veicolo, identificarne la targa e poi anche di leggerne il contenuto. Successivamente, la targa viene confrontata con un elenco di veicoli che sono autorizzati; se il veicolo risulta registrato e autorizzato,  allora l’accesso viene consentito, altrimenti viene negato. 

L’hardware previsto per la realizzazione comprende una S32 Cam oppure, in alternativa, un Raspberry Pi dotato di videocamera, posizionata all'entrata della struttura. I frame catturati dalla camera vengono poi mandati a un server centrale che permette di elaborare le immagini, riconoscere la targa e determinare automaticamente se il veicolo può accedere alla struttura. 

# 2\. Obiettivi e Scopo 

### 2.1 Obiettivi

L’obiettivo principale del progetto è automatizzare il controllo degli accessi a una struttura, eliminando la necessità di un operatore umano.  
Per raggiungere questo scopo, il sistema si articola in una serie di obiettivi funzionali di supporto, che cooperano per garantire un funzionamento affidabile e modulare:

* Rilevamento dei veicoli presenti all’interno di ogni frame acquisito dalla telecamera;  
* Classificazione della tipologia di veicolo (es. automobile, motocicletta, bicicletta);  
* Localizzazione della targa nel caso di veicoli a quattro ruote;   
* Lettura del testo della targa tramite OCR, minimizzando gli errori di riconoscimento;  
* Gestione del sistema tramite un'interfaccia dedicata, che permette:   
  * l’aggiunta oppure la rimozione di veicoli autorizzati;   
  * l’attivazione o disattivazione in maniera temporanea del sistema;   
  * monitoraggio dello stato di funzionamento del sistema;   
* Salvataggio dei dati (quindi targhe, timestamp, ecc) in un archivio locale, per analisi successive o altri scopi;   
* Scalabilità del sistema per permettere futuri miglioramenti, aggiornamenti o integrazioni con altri moduli o dispositivi hardware. 

### 2.2 Benefici

L’adozione di questo nostro sistema comporta numerosi vantaggi, in termini di efficienza, sicurezza e automazione del controllo degli accessi ad un determinato ambiente.   
Più in particolare il sistema permette: 

* L’automatizzazione del controllo dei veicoli in ingresso alla struttura, eliminando quindi la necessità di personale;   
* L’impedimento d’ingresso a veicoli che non sono autorizzati, garantendo così un maggiore livello di sicurezza e un monitoraggio costante di tutti accessi;   
* La registrazione dei veicoli che transitano, consentendo la creazione di uno storico consultabile;   
* L’ottimizzazione della gestione delle risorse in modo tale da migliorare la fluidità del traffico, in prossimità dell’ingresso alla struttura interessata. 

# 3\. Contesto e ambito 

### 3.1 Contesto

Il sistema si inserisce in un contesto di videosorveglianza e monitoraggio automatico dei veicoli, dove le tecnologie di computer vision, intelligenza artificiale vengono impiegate con lo scopo di automatizzare il controllo degli accessi e migliorare la sicurezza. L’obiettivo è quello di ridurre l'intervento dell'uomo, assicurando allo stesso tempo rapidità e affidabilità nell’identificare i veicoli autorizzati. 

Il progetto è stato sviluppato in particolare per l’ambiente scolastico, in modo tale da gestire in modo automatico l’ingresso dei veicoli di docenti, personale autorizzato e studenti che utilizzano mezzi a due ruote. La sua architettura è comunque facilmente adattabile ad altri contesti, quali parcheggi privati o delle strutture aziendali. 

### 3.2 Ambito

Il nostro sistema comprende tutte le funzionalità che sono necessarie per permettere l’analisi automatica dei frame tratti dalla videocamera, con l’obiettivo di rilevare i veicoli in transito, localizzare le targhe e leggerle e gestire l'accesso alla struttura. Questo prevede anche un’interfaccia utente per il monitoraggio e la gestione del sistema, con la possibilità di salvare i dati delle targhe riconosciute in un archivio locale per finalità di consultazione o di analisi.   
Rimangono escluse dall’ambito del progetto le seguenti funzionalità:

* Gestione della sanzione in caso di infrazioni;  
* Integrazione con sistema di sicurezza nazionali, quali banche dati di targhe rubate;  
* Elaborazione immagini in condizioni estreme come pioggia intensa o nebbia fitta.

### 3.3 Componenti e attori principali

| Componente / Attore | Ruolo | Descrizione |
| :---- | :---- | :---- |
| S32 cam / Raspberry Pi con fotocamera | Hardware | Dispositivo acquisizione video incaricato della cattura dei frame dei veicoli in avvicinamento all’ingresso della struttura |
| Sistema di elaborazione | Software | Modulo principale che elabora i frame ricevuti, rileva e classifica i veicoli, localizza e legge le targhe e verifica l’autorizzazione all’accesso |
| Database / Archivio | Storage | Sistema di memorizzazione dei dati delle targhe rilevate, utile per consultazioni, statistiche o tracciabilità degli accessi |
| Amministratori | Gestori | Utenti responsabili della configurazione e gestione del sistema, dell'inserimento o rimozione dei veicoli autorizzati e del monitoraggio del funzionamento |
| Programmatore | Supporto tecnico | Responsabile tecnico incaricato di risolvere eventuali bug, aggiornare il software e integrare nuove funzionalità |

# 4\. Requisiti Funzionali 

| *ID* | Requisito | Descrizione |
| :---- | :---- | :---- |
| *RF-01* | Rilevazione veicoli | Il sistema deve essere in grado di rilevare la presenza di veicoli all’interno di ciascun frame acquisito. |
| *RF-02* | Classificazione veicoli | I veicoli rilevati devono essere classificati sulla base della tipologia del veicolo (auto, camion, moto, bicicletta, ecc.) |
| *RF-03* | Localizzazione targhe | Il sistema deve individuare in modo preciso la regione dell’immagine contenente la targa del veicolo (se a 4 ruote) |
| *RF-04* | Lettura targhe OCR | Il sistema deve essere in grado di leggere e trascrivere in formato testuale il contenuto della targa individuata, riducendo gli errori di riconoscimento |
| *RF-05* | Salvataggio dati | Il sistema deve memorizzare le targhe rilevate specificando il timestamp e lo stato di autorizzazione |
| *RF-06* | Gestione utenti autorizzati | Il sistema offre un’interfaccia grafica che consente agli amministratori di aggiungere, modificare o rimuovere veicoli autorizzati |
| *RF-07* | Autenticazione amministratori | La gestione del sistema è autorizzata solo ad utenti autenticati con credenziali amministrative |

# 5\. Requisiti non Funzionali  

| Categoria | ID | Requisito | Descrizione |
| :---- | :---- | :---- | :---- |
| Prestazioni | *RNF-01* | Analisi in tempo reale | Il sistema deve elaborare i frame in real-time, con un tempo di processamento per veicolo non superiore a 3 secondi |
|  | *RNF-02* | Tempo di risposta | La rilevazione e lettura della targa devono avvenire con latenza minima per garantire efficienza |
| Usabilità | *RNF-03* | Interfaccia grafica | Il sistema dispone di un’interfaccia utente per la gestione del sistema, inclusa la configurazione dei veicoli autorizzati e attivazione/disattivazione del servizio |
|  | *RNF-04* | Funzioni di log e report  | Il sistema genera automaticamente log e report consultabili per il monitoraggio del servizio |
| Tecnologici | *RNF-05* | Linguaggio | Il sistema deve essere sviluppato in Python 3.10 o versioni superiori |
|  | *RNF-06* | Hardware | Utilizzo di camera con buona qualità di acquisizione video; il sistema deve supportare l’accelerazione tramite GPU se disponibile |
| Manutenibilità | *RNF-07* | Architettura modulare | Il codice deve essere organizzate in moduli e funzioni separati per facilitare la manutenzione e debugging |
|  | *RNF-08* | Scalabilità | Deve essere possibile estendere le funzionalità, aggiungere nuovi filtri di elaborazione o integrazioni future con altri sistemi |

# 6\. Analisi dei rischi e criticità 

| Rischio | Gravità | Risoluzione |
| :---- | :---- | :---- |
| Qualità video scadente | Alta | Sostituire la videocamera con un dispositivo di acquisizione di qualità superiore o regolare parametri di esposizione e risoluzione per migliorare la nitidezza dei frame |
| Condizioni di luce variabili | Media | Implementazione tecniche di pre-processing dei frame per migliorare la rilevazione e lettura delle targhe |
| Condizioni metereologiche estreme (pioggia intensa o nebbia fitta) | Alta | Prevedere metodi alternativi di accesso alla struttura, come sistemi di badge o tessere |
| Velocità di elaborazione insufficiente per il real-time | Media | Revisione e ottimizzazione del codice e utilizzo di sistemi hardware dotati di GPU per accelerare l’elaborazione dei frame  |

# 7\. Diagramma caso d’uso 
Puoi vederlo direttamente dal PDF.