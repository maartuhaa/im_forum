# IM Student Forum

IM Student Forum er en webbasert diskusjonsplattform utviklet med Flask og MariaDB.  
Applikasjonen lar elever opprette innlegg, samhandle med andre og utforske temaer innen programmering i et rent og moderne grensesnitt.

---

## Funksjoner

- Brukerautentisering (registrering, innlogging, utlogging)
- Opprette og vise innlegg
- Like-system (like/unlike per bruker)
- Brukerprofiler med egne innlegg
- Moderne UI med popup-vinduer (innlogging, registrering, visning av innlegg)
- Responsivt design

---

## Teknologier

- **Backend:** Flask (Python)
- **Database:** MariaDB (MySQL)
- **Frontend:** HTML, CSS, JavaScript
- **Autentisering:** Flask sessions + passord-hashing

---

## Databasestruktur

### Brukere
- id
- username
- email
- password
- created_at

### Innlegg
- id
- title
- content
- user_id
- theme_id (valgfritt)
- created_at

### Likes på innlegg
- id
- user_id
- post_id

### Kommentarer 
- id
- content
- user_id
- post_id
- created_at

---

## 🔐 Cybersikkerhet – Yrkesfaglig fordypning

I dette prosjektet har jeg brukt grunnleggende prinsipper fra cybersikkerhet for å gjøre forumet sikrere.

Passord lagres som hash ved hjelp av `werkzeug.security`, slik at de ikke lagres i klartekst i databasen. Kun innloggede brukere kan like innlegg og skrive kommentarer, noe som kontrolleres gjennom sessions i backend.

For å beskytte mot angrep bruker jeg parameteriserte SQL-spørringer (`%s`) for å forhindre SQL injection, samt Jinja2 escaping (`|escape`) for å redusere risikoen for XSS.

Databasen er også strukturert slik at en bruker ikke kan like samme innlegg flere ganger, ved å bruke en egen tabell for likes.

Dette viser hvordan grunnleggende sikkerhet kan implementeres i praksis i en webapplikasjon.

---

## Installasjon

1. Klon repository:
git clone https://github.com/maartuhaa/im_forum.git
