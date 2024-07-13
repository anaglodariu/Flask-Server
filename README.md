Nume: Glodariu Ana
Grupă: 331CB

# Tema <1>

Organizare
-
1. Explicație pentru soluția aleasă:

    * am ales să citesc datele din csv linie cu linie pentru a nu face încărcarea întregului
    fișier în memorie odată, folosindu-mă de funcția ***csv.DictReader***
    * am reținut doar datele de care aveam nevoie pentru request-uri la server și am creat un
    dicționar de forma:
    {
        'state': {
            'question': {
               '(stratification category, stratification)': [data_value1, data_value2, ...]
            }
            ...
        }
        ...
    }

    * toate thread-urile vor face în paralel job-uri primite de thread pool și nu e nevoie de
    sincronizare la nivel de date deoarece fiecare thread va avea variabila sa locală cu datele
    despre job, va calcula apoi rezultatul într-o variabilă locală ***res*** și va scrie
    rezultatul într-un fișier de ieșire
    * sincronizarea a fost necesară la shutdown-ul thread pool-ului pentru a nu rămâne cu job-uri
    neterminate sau cu thread-uri blocate în așteptarea unui job
    * pentru a semnala că un job a fost terminat am folosit funțiile din biblioteca queue
    ***get()***,  ***task_done()*** și ***join()*** pentru a aștepta ca toate job-urile să fie
    terminate
    * pentru fiecare get() al unui job din coadă, am adăugat un task_done() pentru a semnala că
    job-ul a fost terminat
    * înainte de a lua un job din coadă, am introdus o variabilă condiție ***self.job_available***
    comună tuturor thread-urilor pentru a semnala că există job-uri disponibile în coadă sau că s-a
    dat semnal de shutdown, altfel thread-urile s-ar fi putut bloca la get() dacă nu existau
    job-uri în coadă
    * pentru a semnala shutdown-ul thread pool-ului am folosit o variabilă event
    ***self.terminate*** comună tututor thread-urilor a cărui flag este setat pe true când
    se dă graceful shutdown
    * atunci când se primește graceful shutdown vor avea loc următoarele acțiuni:
        * se așteaptă ca pentru fiecare job din coadă să se apeleze task_done() cu ajutorul lui
        join() aplicat pe coadă, astfel încât ne asigurăm că nu mai există job-uri în coadă când 
        setăm pe true flag-ul event-ului de shutdown
        * se setează flag-ul event-ului ***self.shutdown_event*** pe true
        * sunt notificate toate thread-urile care așteaptă după un job din coadă cu wait_for()
        * cănd se verifică valoarea flag-ului event-ului de shutdown, thread-urile se închid

    * pentru fiecare request de tip post, mai întâi se pregătesc datele necesare realizării
    job-ului ce va fi trimis către thread pool pentru a fi procesat, iar apoi se creează
    funcția lambda ce va fi aplicată pe acele date
    * astfel, atunci când ajunge job-ul la un thread, acesta va apela funcția lambda cu datele
    primite și va scrie rezultatul în fișierul de ieșire
    * am înglobat funcționalitatea unui job într-un dicționar, ca atunci când
    este trimis către thread pool, să fie ușor de accesat și de procesat de către thread-uri

***Utilitatea temei*** 

Consider că tema a fost utilă pentru că nu am folosit numai
noțiuni de sincronizare a thread-urilor, ci și de realizare
request-uri către un server + logging + unittesting.

***Complexitate implementare*** 

Consider că stocarea doar a datelor necesare într-o structură de tip dicționar este o abordare
eficientă datorită accesului rapid la datele necesare în cadrul request-urilor către server.
Pentru fiecare request de tip post, îmi creez noi variabile de tip dicționar (cu referințe la
structura de date inițială) pentru a stoca doar datele necesare pentru job-ul respectiv => acces
rapid la datele necesare + reducerea memoriei folosite.

***Cazuri speciale, nespecificate în enunț:***

Am tratat doar unele cazuri în care statul sau întrebarea nu există în csv-ul de date, în care
returnez ***return {"status": "Invalid question"} sau {"status": "Invalid state"}*** și creez 
un mesaj de log de tip ***error***.

Implementare
-

Întregul enunț al temei a fost implementat.

* Dificultăți întâmpinate:

    * implementarea părții de drain mode al job-urilor din coadă când se
primea gracefull shutdown, deoarece trebuia să mă asigur că toate job-urile sunt terminate și că
niciun thread nu se blochează așteptând după un job din coadă.
    * implementarea unittest-urilor din cauza importurilor, atunci când încerc să rulez
unittest-urile mi se rulează totul din fișierul __init__.py și se deschide server-ul sau există
erori de import, deci pentru a rezolva problema a trebuit:
    * să îmi creez un fișier separat în app denumit operations.py în care să îmi mut din routes.py
funcțiile folosite în evaluarea job-urilor
    * să îmi creez o variabilă de mediu pe care o setez în fișierul cu unitteste și o verific
în fișierul __init__.py pentru a nu se mai deschide serverul (m-am inspirat din folosirea
variabilei de mediu TP_NUM_OF_THREADS)

* Resurse utilizate:

https://docs.python.org/3/library/queue.html
https://ocw.cs.pub.ro/courses/asc/laboratoare/03
https://docs.python.org/3/library/logging.html
https://docs.python.org/3/library/unittest.html
