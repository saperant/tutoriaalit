# 0002. Lukemat tallennetaan SQLiteen

- Tila: korvattu (ks. 0003)
- Päivä: 2026-04-20

## Tausta

Ensimmäisessä vaiheessa asemia on viisi ja palvelimia yksi. Ylläpitoon
ei ole omaa henkilöä.

## Päätös

Tallennamme lukemat SQLite-tiedostoon palvelimen levylle.

## Seuraukset

Erillistä tietokantapalvelinta ei tarvitse asentaa eikä valvoa.
Varmuuskopio on yksi tiedosto. Vain yksi prosessi voi kirjoittaa
kerrallaan, joten palvelua ei voi monistaa usealle koneelle.
