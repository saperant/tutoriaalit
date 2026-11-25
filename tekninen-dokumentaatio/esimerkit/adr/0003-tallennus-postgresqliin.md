# 0003. Lukemat tallennetaan PostgreSQL:ään

- Tila: hyväksytty
- Päivä: 2026-10-08
- Korvaa: 0002

## Tausta

Asemia on nyt 60, ja yhteenvetoja kysytään kahdesta palvelusta yhtä
aikaa. Kirjoitukset jonoutuvat SQLiten tiedostolukon takia, ja
lukemia on hylätty aikakatkaisun vuoksi kolmesti syyskuussa.

## Päätös

Siirrämme lukemat PostgreSQL:ään. Vanhat lukemat tuodaan kertaajona.

## Seuraukset

Useampi palvelu voi lukea ja kirjoittaa yhtä aikaa. Tietokantapalvelin
on valvottava ja päivitettävä: hälytykset ja toimintaohje lisätään
samassa muutoksessa. Varmuuskopiointi muuttuu tiedoston kopioinnista
tietokannan vedokseksi. Aikasarjatietokanta hylättiin, koska
lukemamäärä (noin 1500 riviä päivässä) ei vaadi sitä.
