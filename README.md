# Wedify

**Wedify** je studentski projekt iz kolegija **Informacijski sustavi**. Projekt izrađuju **Mateo Kruljac** i **Petra Podunavac**, studenti 1. godine izvanrednog online prijediplomskog studija Informatike na Fakultetu informatike u Puli, Sveučilište Jurja Dobrile u Puli.

Aplikacija je zamišljena kao jednostavan informacijski sustav za upravljanje salama za vjenčanja, rezervacijama i osnovnom analitikom poslovanja. Cilj aplikacije je prikazati kako se podaci mogu unositi, uređivati, spremati, povezivati i kasnije koristiti za pregled poslovanja.

Wedify omogućuje da se podaci o salama i rezervacijama vode na jednom mjestu, uz pregledan dizajn, jasne statuse rezervacija i grafički prikaz najvažnijih poslovnih pokazatelja.

---

## Opis projekta

Wedify služi za vođenje osnovnih podataka o salama za vjenčanja i rezervacijama. U stvarnom radu takvi se podaci često vode ručno, kroz bilježnice, poruke ili tablice, pa se lako može dogoditi da se neki podatak zaboravi, krivo upiše ili da se isti termin pokuša rezervirati više puta.

Aplikacija omogućuje da se svi bitni podaci nalaze na jednom mjestu. Korisnik može dodavati sale, pregledavati postojeće sale, unositi rezervacije za određene datume, pratiti status rezervacije i kroz analitiku vidjeti osnovne pokazatelje poslovanja.

Osnovna ideja aplikacije je jednostavna: korisnik najprije unese sale koje ima na raspolaganju, zatim za te sale izrađuje rezervacije, a aplikacija na temelju tih podataka prikazuje pregled poslovanja.

---

## Funkcionalnosti aplikacije

Aplikacija je podijeljena u nekoliko glavnih dijelova:

- početna stranica
- sale
- rezervacije
- analitika
- odabir datuma kroz kalendar u formi rezervacije
- pretraga, filtriranje i sortiranje
- paginacija podataka
- vizualni prikaz statusa rezervacija

Svaki dio aplikacije ima svoju ulogu u informacijskom sustavu. Sale predstavljaju prostore koji se mogu rezervirati, rezervacije predstavljaju konkretne događaje, a analitika koristi unesene podatke za prikaz poslovnog pregleda.

---

## Početna stranica

Početna stranica prikazuje **nadolazeće odobrene rezervacije**. Time korisnik odmah po otvaranju aplikacije vidi najbliže potvrđene termine.

Za svaku nadolazeću rezervaciju prikazuju se:

- naziv sale
- imena mladenke i mladoženje
- datum rezervacije
- broj gostiju

Početna stranica je namjerno pojednostavljena kako bi se korisniku odmah prikazale najvažnije informacije bez pretrpanog sučelja.

---

## Sale

Dio **Sale** omogućuje pregled svih unesenih sala. Za svaku salu prikazuju se:

- naziv sale
- lokacija
- kapacitet
- cijena najma

Korisnik može dodati novu salu, urediti postojeću salu ili obrisati salu koja više nije potrebna u sustavu. Popis sala može se pretraživati i sortirati, što olakšava rad kada je uneseno više zapisa.

Sale su važan dio sustava jer se svaka rezervacija veže uz jednu konkretnu salu. Na taj se način zna gdje se pojedino vjenčanje održava, koliki je kapacitet prostora i koja je cijena najma.

---

## Rezervacije

Dio **Rezervacije** povezuje sale s konkretnim događajima. Kod unosa nove rezervacije korisnik bira salu, datum, unosi podatke o mladenki i mladoženji, njihove kontakte, broj gostiju i status rezervacije.

Datum rezervacije odabire se kroz kalendar u polju za datum. To olakšava unos jer korisnik ne mora ručno pisati datum, nego ga jednostavno odabere iz kalendarskog prikaza. Time je unos pregledniji i smanjuje se mogućnost pogreške pri upisu datuma.

Za svaku rezervaciju evidentiraju se:

- odabrana sala
- datum rezervacije
- ime i prezime mladenke
- ime i prezime mladoženje
- kontakt mladenke
- kontakt mladoženje
- broj gostiju
- cijena najma
- status rezervacije

Aplikacija ne dopušta spremanje odobrene rezervacije ako za istu salu i isti datum već postoji druga odobrena rezervacija. Time se sprječava dvostruka rezervacija istog termina.

Status rezervacije može biti:

- **Odobrena**
- **Nije odobrena**

Odobrene rezervacije prikazane su zelenom bojom, a neodobrene crvenom bojom. Time korisnik odmah vidi koji su termini potvrđeni, a koji su još u dogovoru.

---

## Analitika

Dio **Analitika** prikazuje osnovni pregled poslovanja na temelju unesenih podataka. Analitika koristi podatke iz baze i prikazuje ih kroz kartice i grafove.

Analitika prikazuje:

- ukupan broj rezervacija
- broj odobrenih rezervacija
- broj neodobrenih rezervacija
- stopu odobrenja
- ukupan broj sala
- prihod od odobrenih rezervacija
- prosječan broj gostiju
- broj nadolazećih rezervacija
- najpopularnije sale
- status rezervacija
- prihod po mjesecima
- broj vjenčanja po mjesecu

Grafovi pomažu da se lakše vidi koje su sale najpopularnije, kakav je odnos odobrenih i neodobrenih rezervacija te kako se prihodi kreću po mjesecima.

Analitika je važna jer podatke iz sustava pretvara u pregledne informacije. Korisnik ne mora ručno brojati rezervacije ili računati prihod, nego aplikacija iz već unesenih podataka prikazuje osnovni poslovni pregled.

---

## CRUD funkcionalnosti

Aplikacija koristi osnovni **CRUD** princip rada nad podacima. CRUD označava dodavanje, pregled, uređivanje i brisanje zapisa.

U projektu se CRUD koristi za dvije glavne cjeline: **sale** i **rezervacije**. Korisnik može dodavati nove sale i rezervacije, pregledavati postojeće podatke, uređivati ih po potrebi i brisati zapise koji više nisu potrebni.

CRUD funkcionalnosti čine osnovu aplikacije jer omogućuju jednostavno upravljanje glavnim podacima u sustavu.

---

## Pretraga, filtriranje i sortiranje

Aplikacija omogućuje lakši rad s većim brojem podataka kroz pretragu, filtriranje i sortiranje.

Kod sala se može pretraživati i sortirati prema podacima kao što su naziv, lokacija, kapacitet i cijena.

Kod rezervacija se mogu koristiti filteri i pretraga kako bi korisnik brže pronašao određeni zapis. To je posebno korisno kada se u sustavu nalazi veći broj rezervacija.

---

## Paginacija

Aplikacija koristi paginaciju kako bi se podaci prikazivali preglednije. Umjesto da se svi zapisi prikažu odjednom, prikazuje se ograničen broj zapisa po stranici.

U aplikaciji je podešeno da se prikazuje **8 zapisa po stranici**. Kod većeg broja rezervacija paginacija prikazuje samo najvažnije brojeve stranica, uz mogućnost prelaska na prethodnu i sljedeću stranicu.

Time se izbjegava nepregledan prikaz velikog broja zapisa.

---

## Validacija i poslovna pravila

Aplikacija ima osnovna pravila koja pomažu u smanjenju pogrešaka pri unosu podataka.

Primjeri pravila:

- obavezna polja moraju biti popunjena
- datum rezervacije odabire se kroz kalendar u formi za unos
- broj gostiju ne smije prelaziti kapacitet odabrane sale
- odobrena rezervacija zauzima termin
- za istu salu i isti datum ne mogu postojati dvije odobrene rezervacije
- status rezervacije jasno se prikazuje korisniku
- korisnik dobiva poruku nakon uspješnog dodavanja, uređivanja ili brisanja

Ova pravila čine aplikaciju praktičnijom za stvarno korištenje jer smanjuju mogućnost pogrešnog unosa i dvostrukog zauzimanja termina.

---

## Dizajn aplikacije

Dizajn aplikacije prilagođen je temi vjenčanja. Korištene su nježne boje, zaobljeni elementi, kartice i vizualno odvojeni statusi.

Statusi rezervacija prikazani su bojama:

- zelena boja za odobrene rezervacije
- crvena boja za neodobrene rezervacije

Cilj dizajna je da aplikacija bude pregledna, jednostavna za korištenje i vizualno povezana s temom svadbenih rezervacija.

---

## CRUD dijagram

CRUD dijagram projekta dostupan je na poveznici:

https://lucid.app/lucidchart/8226c84d-962a-412d-b1f9-6aa5be3504f2/edit?invitationId=inv_3d17d1e0-b4fe-4bfc-bae7-507fb82fb835&page=2hjuQuuR1M9ZV#

---

## Tehnologije

Projekt koristi sljedeće tehnologije:

- Python
- Flask
- Pony ORM
- SQLite
- HTML
- CSS
- Bootstrap
- JavaScript
- Chart.js
- Docker
- Docker Compose

Aplikacija koristi SQLite bazu podataka, koja se nalazi u datoteci `wedding.db`. To je praktično za studentski projekt jer se baza nalazi u jednoj datoteci i ne zahtijeva posebno podešavanje većeg sustava za bazu podataka.

Pony ORM koristi se za povezivanje Python modela sa SQLite bazom podataka i za jednostavniji rad s podacima o salama i rezervacijama.

---

## Struktura projekta

Najvažnije datoteke i direktoriji u projektu su:

```text
Dockerfile
docker-compose.yml
requirements.txt
run.py
factory.py
config.py
helpers.py
models.py
blueprints/
templates/
static/
wedding.db
```

Kratko objašnjenje:

```text
Dockerfile - definira Docker image za pokretanje aplikacije
docker-compose.yml - definira način pokretanja containera
requirements.txt - popis Python paketa potrebnih za rad aplikacije
run.py - datoteka za pokretanje aplikacije
factory.py - stvaranje Flask aplikacije
config.py - osnovne konfiguracijske postavke aplikacije
helpers.py - pomoćne funkcije
models.py - modeli podataka i rad s bazom
blueprints/ - rute i logika aplikacije po dijelovima
templates/ - HTML predlošci
static/ - CSS, JavaScript i slike
wedding.db - SQLite baza podataka
```

---

## Organizacija koda

Projekt je organiziran kroz više dijelova kako bi kod bio pregledniji.

Direktorij `blueprints/` sadrži logiku aplikacije podijeljenu po funkcionalnostima:

```text
analytics.py - logika za analitiku
halls.py - logika za sale
main.py - početna stranica
reservations.py - logika za rezervacije
```

Direktorij `templates/` sadrži HTML predloške koji određuju izgled stranica.

Direktorij `static/` sadrži CSS, JavaScript i slike koje se koriste za dizajn i interaktivnost aplikacije.

---

## Baza podataka

Podaci se spremaju u SQLite bazu podataka:

```text
wedding.db
```

Baza sadrži podatke o salama i rezervacijama. Rezervacija je povezana sa salom, što omogućuje da se za svaku rezervaciju zna u kojoj se sali održava događaj.

Glavne cjeline baze su:

- sale
- rezervacije

Sale predstavljaju prostore koji se mogu rezervirati, a rezervacije predstavljaju konkretne događaje povezane s tim salama.

---

## Pokretanje aplikacije lokalno

Za pokretanje aplikacije potrebno je imati instaliran **Docker Desktop**.

Projekt se najprije preuzima s GitHuba:

```bash
git clone https://github.com/Mateokruljac/weeding-book.git
cd weeding-book
```

Aplikacija se pokreće naredbom:

```bash
docker compose up --build
```

Nakon pokretanja aplikacija je dostupna u pregledniku na adresi:

```text
http://localhost:5000
```

Za zaustavljanje aplikacije u terminalu se pritisne:

```text
CTRL + C
```

Nakon toga se container može ugasiti naredbom:

```bash
docker compose down
```

---

## Napomena o Docker pokretanju

Aplikacija se pokreće unutar Docker containera. U datoteci `docker-compose.yml` mapiran je port:

```yaml
ports:
  - "5000:5000"
```

To znači da aplikacija radi na portu 5000 unutar containera i dostupna je na računalu preko adrese:

```text
http://localhost:5000
```

U datoteci `run.py` Flask aplikacija se pokreće s hostom `0.0.0.0`, kako bi bila dostupna izvan containera:

```python
app.run(
    host="0.0.0.0",
    port=5000,
    debug=True,
    use_reloader=not in_docker,
    reloader_type="stat",
)
```

---

## Mogući daljnji razvoj

Aplikacija je napravljena kao studentski projekt i predstavlja osnovnu funkcionalnu verziju informacijskog sustava. U stvarnom korištenju mogla bi se dodatno proširiti.

Moguće nadogradnje su:

- prijava korisnika
- različite korisničke uloge
- evidencija uplata i akontacija
- slanje potvrde rezervacije e-mailom
- izvoz potvrde rezervacije u PDF
- detaljniji izvještaji
- dodatne usluge uz rezervaciju
- evidencija menija, dekoracija i posebnih zahtjeva
- prelazak na veću bazu podataka, primjerice PostgreSQL ili MySQL

Ove nadogradnje nisu nužne za osnovni rad aplikacije, ali bi bile korisne kada bi se aplikacija koristila u stvarnom poslovnom okruženju.

---

## Zaključak

Wedify prikazuje osnovnu ideju informacijskog sustava za upravljanje salama i rezervacijama za vjenčanja. Kroz aplikaciju se mogu unositi i uređivati sale, izrađivati rezervacije, pratiti status rezervacija i analizirati osnovni pokazatelji poslovanja.

Projekt povezuje poslovnu ideju i tehničku izvedbu. S poslovne strane rješava problem organizacije sala i termina, a s tehničke strane prikazuje rad web aplikacije, baze podataka i Docker okruženja.

Aplikacija je jednostavna, pregledna i dovoljno funkcionalna za prikaz osnovnog toka rada: unos sala, izrada rezervacija, spremanje podataka i prikaz analitike.
