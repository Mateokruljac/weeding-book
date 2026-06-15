# Wedify

**Wedify** je studentski projekt iz kolegija **Informacijski sustavi**. Projekt izrađuju **Mateo Kruljac** i **Petra Podunavac**, studenti 1. godine izvanrednog online prijediplomskog studija Informatike na Fakultetu informatike u Puli, Sveučilište Jurja Dobrile u Puli.

Aplikacija je zamišljena kao jednostavan informacijski sustav za upravljanje salama za vjenčanja, rezervacijama i osnovnom analitikom poslovanja. Cilj aplikacije je prikazati kako se podaci mogu unositi, uređivati, spremati, povezivati i kasnije koristiti za pregled poslovanja.

---

## Opis projekta

Wedify služi za vođenje osnovnih podataka o salama za vjenčanja i rezervacijama. U stvarnom radu takvi se podaci često vode ručno, kroz bilježnice, poruke ili tablice, pa se lako može dogoditi da se neki podatak zaboravi, krivo upiše ili da se isti termin pokuša rezervirati više puta.

Aplikacija zato omogućuje da se svi bitni podaci nalaze na jednom mjestu. Korisnik može dodavati sale, pregledavati postojeće sale, unositi rezervacije za određene datume, pratiti status rezervacije i na kraju kroz analitiku vidjeti osnovne pokazatelje poslovanja.

Osnovna ideja aplikacije je jednostavna: korisnik najprije unese sale koje ima na raspolaganju, zatim za te sale izrađuje rezervacije, a aplikacija na temelju tih podataka prikazuje pregled poslovanja.

---

## Funkcionalnosti aplikacije

Aplikacija je podijeljena u nekoliko glavnih dijelova.

### Početna stranica

Početna stranica služi kao ulaz u aplikaciju. Korisniku su odmah ponuđene dvije glavne mogućnosti: pregled sala i izrada nove rezervacije.

### Sale

Dio **Sale** omogućuje pregled svih unesenih sala. Za svaku salu prikazuju se:

- naziv sale
- lokacija
- kapacitet
- cijena najma

Korisnik može dodati novu salu, urediti postojeću salu ili obrisati salu koja više nije potrebna u sustavu. Popis sala može se pretraživati i sortirati, što olakšava rad kada je uneseno više zapisa.

Ovaj dio aplikacije prikazuje osnovni **CRUD** princip rada: dodavanje, pregled, izmjena i brisanje podataka.

### Rezervacije

Dio **Rezervacije** povezuje sale s konkretnim događajima. Kod unosa nove rezervacije korisnik bira salu, datum, unosi podatke o mladenki i mladoženji, njihove kontakte, broj gostiju i status rezervacije.

Aplikacija ne dopušta spremanje odobrene rezervacije ako za istu salu i isti datum već postoji druga odobrena rezervacija. Time se sprječava dvostruka rezervacija istog termina.

Status rezervacije može biti odobren ili neodobren, što omogućuje razlikovanje potvrđenih rezervacija od onih koje su još u dogovoru.

### Analitika

Dio **Analitika** prikazuje osnovni pregled poslovanja na temelju unesenih podataka. Prikazuju se podaci kao što su:

- ukupan broj rezervacija
- broj odobrenih rezervacija
- broj neodobrenih rezervacija
- stopa odobrenja
- ukupan broj sala
- prihod od odobrenih rezervacija
- prosječan broj gostiju
- nadolazeće rezervacije

Osim brojčanih pokazatelja, aplikacija prikazuje i grafove. Grafovi pomažu da se lakše vidi koje su sale najpopularnije, kakav je odnos odobrenih i neodobrenih rezervacija te kako se prihodi kreću po mjesecima.

---

## CRUD dijagram

CRUD dijagram projekta dostupan je na poveznici:

https://lucid.app/lucidchart/8226c84d-962a-412d-b1f9-6aa5be3504f2/edit?invitationId=inv_3d17d1e0-b4fe-4bfc-bae7-507fb82fb835&page=2hjuQuuR1M9ZV#

---

## Tehnologije

Projekt koristi sljedeće tehnologije:

- Python
- Flask
- SQLite
- HTML
- CSS
- Bootstrap
- JavaScript
- Docker
- Docker Compose

Aplikacija koristi SQLite bazu podataka, koja se nalazi u datoteci `wedding.db`. To je praktično za studentski projekt jer se baza nalazi u jednoj datoteci i ne zahtijeva posebno podešavanje većeg sustava za bazu podataka.

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
models.py - modeli podataka i rad s bazom
helpers.py - pomoćne funkcije
blueprints/ - rute i logika aplikacije po dijelovima
templates/ - HTML predlošci
static/ - CSS, JavaScript i slike
wedding.db - SQLite baza podataka
```

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
- napredniji kalendarski prikaz zauzetih termina
- evidencija uplata i akontacija
- slanje potvrde rezervacije e-mailom
- detaljniji izvještaji
- dodatne usluge uz rezervaciju
- evidencija menija, dekoracija i posebnih zahtjeva
- prelazak na veću bazu podataka, primjerice PostgreSQL ili MySQL

Ove nadogradnje nisu nužne za osnovni rad aplikacije, ali bi bile korisne kada bi se aplikacija koristila u stvarnom poslovnom okruženju.

---

## Zaključak

Wedify prikazuje osnovnu ideju informacijskog sustava za upravljanje salama i rezervacijama za vjenčanja. Kroz aplikaciju se mogu unositi i uređivati sale, izrađivati rezervacije, pratiti status rezervacija i pregledavati osnovna analitika.

Projekt povezuje poslovnu ideju i tehničku izvedbu. S poslovne strane rješava problem organizacije sala i termina, a s tehničke strane prikazuje rad web aplikacije, baze podataka i Docker okruženja.

Aplikacija je jednostavna, pregledna i dovoljno funkcionalna za prikaz osnovnog toka rada: unos sala, izrada rezervacija, spremanje podataka i prikaz analitike.
