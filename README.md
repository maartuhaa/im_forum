# IM Student Forum

IM Student Forum is a web-based discussion platform built with Flask and MariaDB.  
The application allows students to create posts, interact with others, and explore programming-related topics in a clean and modern interface.

---

## Features

- User authentication (register, login, logout)
- Create and view posts
- Like system (toggle like/unlike per user)
- User profiles with personal posts
- Modern UI with modal popups (login, register, post view)
- Responsive layout

---

## Tech Stack

- **Backend:** Flask (Python)
- **Database:** MariaDB (MySQL)
- **Frontend:** HTML, CSS, JavaScript
- **Authentication:** Flask sessions + password hashing

---

## Database Structure

### Users
- id
- username
- email
- password
- created_at

### Posts
- id
- title
- content
- user_id
- theme_id (optional)
- created_at

### Post Likes
- id
- user_id
- post_id

### Comments (planned / optional)
- id
- content
- user_id
- post_id
- created_at

---

## Cyber Security – Yrkesfaglig fordypning

I dette prosjektet har jeg brukt grunnleggende prinsipper fra cybersecurity for å gjøre forumet sikrere.

Passord lagres som hash ved hjelp av `werkzeug.security`, slik at de ikke ligger i klartekst i databasen. Kun innloggede brukere kan like innlegg og skrive kommentarer, noe som kontrolleres gjennom session i backend.

For å beskytte mot angrep bruker jeg parameteriserte SQL-spørringer (`%s`) for å forhindre SQL injection, samt Jinja2 escaping (`|escape`) for å redusere risiko for XSS.

Databasen er også strukturert slik at en bruker ikke kan like samme innlegg flere ganger, ved å bruke en egen tabell for likes.

Dette viser hvordan grunnleggende sikkerhet kan implementeres i praksis i en webapplikasjon.

---
## Installation

1. Clone the repository:
https://github.com/maartuhaa/im_forum.git
