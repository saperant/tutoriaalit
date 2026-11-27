# Virheilmoitukset ja toipuminen

Suurin osa ohjelmista, joita kääntäjä näkee, on keskeneräisiä tai
virheellisiä: ohjelmoija kirjoittaa, kääntää ja korjaa. Hyvä kääntäjä
löytää virheen, kertoo sen paikan ja syyn ymmärrettävästi ja raportoi
yhdellä ajolla mahdollisimman monta *todellista* virhettä mutta ei
yhtään kuviteltua. Tämä luku käsittelee jäsentimen virheitä;
semanttiset virheet tulevat luvussa 7.

## Virheilmoituksen muoto

Kide kirjoittaa virheet muodossa `tiedosto:rivi:sarake: virhe: viesti`.
Muoto on GCC:n ja Clangin, ja editorit, kehitysympäristöt ja
CI-järjestelmät osaavat poimia siitä sijainnin ja hypätä oikeaan
kohtaan. Kaikki virheet kulkevat yhden olion kautta:

```{.cpp tiedosto="esimerkit/kide/diagnostiikka.hpp" osa="diagnostiikka"}
```

Diagnostiikkaolio myös laskee virheet. Pääohjelma kysyy siltä jokaisen
vaiheen jälkeen, voiko jatkaa, ja tulostaa yhteenvedon. Yläraja estää
tilanteen, jossa yksi rikkinäinen tiedosto tuottaa tuhansia rivejä
virheitä.

Hyvässä viestissä on kaksi osaa: mitä odotettiin ja mitä saatiin.
Jäsentimen viestit muodostetaan automaattisesti `odota`-funktiossa
tokenin lajista (luku 5), joten niistä tulee yhdenmukaisia:
`odotettiin ';', saatiin 'return'`.

## Paniikkitila

Kun jäsennin kohtaa odottamattoman tokenin, se ei tiedä, mikä
ohjelmoijan tarkoitus oli. Yksinkertaisin toipumiskeino on
**paniikkitila** (*panic mode*): hylätään tokeneita, kunnes löytyy
kohta, josta jäsentämistä voi jatkaa luotettavasti. Sellaisia kohtia
ovat lauseen loppu (`;`) ja seuraavan lauseen alku (avainsana tai `}`).

```{.cpp tiedosto="esimerkit/kide/jasennin.cpp" osa="synkronoi"}
```

Virhe nousee poikkeuksena `odota`-funktiosta lohkon silmukkaan, joka
sieppaa sen, synkronoi ja jatkaa seuraavasta lauseesta:

```{.cpp tiedosto="esimerkit/kide/jasennin.cpp" osa="lohko"}
```

Poikkeus sopii tähän hyvin. Virhe voi syntyä syvällä lausekkeen
rekursiossa, ja poikkeus purkaa kaikki keskeneräiset funktiokutsut
kerralla ilman, että jokainen funktio tarkistaa virhekoodin. Poikkeus
on C++:ssa kallis, mutta sitä heitetään vain virheen sattuessa,
ei normaalissa ohjausvuossa. Funktiotasolla on toinen sieppauskohta:
jos funktion otsikko on rikki, hypätään seuraavaan `fn`-sanaan.

Esimerkki, jossa on kolme virhettä:

```{.rust tiedosto="esimerkit/virheet/jasennys.kide"}
```

```{.tuloste tiedosto="esimerkit/virheet/jasennys.virhe"}
```

Kolmas virhe on tyypillinen: puuttuva puolipiste huomataan vasta
seuraavan rivin alussa, koska vasta silloin on varmaa, ettei lause
jatku. Virheen sijainti on siksi `return`-sanan kohdalla, ei rivin 6
lopussa. Clang korjaa tämän ilmoittamalla sijainniksi edellisen
tokenin lopun ja ehdottamalla puolipisteen lisäämistä (*fix-it*).

## Seurannaisvirheet

Toipuminen voi epäonnistua: jos synkronointikohta valitaan huonosti,
jäsennin jatkaa väärästä kohdasta ja raportoi virheitä, joita ei ole.
Tällaiset **seurannaisvirheet** (*cascading errors*) ovat kääntäjien
käyttäjien suurimpia ärsytyksen aiheita. Kide käyttää niitä vastaan
kolmea keinoa:

1. Paniikkitila pysähtyy lauseen rajalle, joten virhe jää yhden
   lauseen sisälle.
2. Selaaja tuottaa virheellisestä luvusta silti luku-tokenin, joten
   jäsennin ei näe aukkoa (luku 3).
3. Semanttinen analyysi antaa virheelliselle lausekkeelle tyypin
   *tuntematon*, joka kelpaa kaikkialle (luku 7).

Neljäs keino on lopettaa ajo vaiheen jälkeen, jos virheitä oli:
semanttista analyysiä ei ajeta puulle, jossa on jäsennysvirheitä,
koska puuttuvat lauseet tuottaisivat vääriä nimivirheitä.

## Syvyysraja

Rekursiivisesti etenevä jäsennin käyttää kutsupinoa, ja syvälle
sisäkkäinen syöte, kuten 100 000 avaavaa sulkua, kaataisi kääntäjän
pinon ylivuotoon. Kääntäjän syöte on käyttäjän dataa, ja kääntäjää
ajetaan myös palvelimilla (Compiler Explorer, kielipalvelimet,
CI), joten kaatuminen on haavoittuvuus. Kide laskee sisäkkäisyyttä
pienellä RAII-luokalla, joka vähentää laskuria myös poikkeuksen
purkaessa pinon:

```{.cpp tiedosto="esimerkit/kide/jasennin.cpp" osa="vartija"}
```

Raja on 200 tasoa. Clang ja GCC käyttävät samaa ajatusta (Clangin
`-fbracket-depth` on oletuksena 256).

## Käytännössä

- **Raportoi ensimmäinen virhe tarkasti; loput ovat bonusta.**
  Ohjelmoija korjaa yleensä ensimmäisen virheen ja kääntää uudelleen.
  Väärät seurannaisvirheet ovat pahempia kuin puuttuvat todelliset.
- **Kerro, mitä odotettiin ja mitä saatiin.** Yhdenmukaiset viestit
  syntyvät, kun ne muodostetaan yhdessä paikassa.
- **Noudata vakiintunutta muotoa.** `tiedosto:rivi:sarake: virhe:`
  toimii kaikissa työkaluissa ilman lisätyötä.
- **Älä kaadu syötteeseen.** Rekursion syvyys, tiedoston koko ja
  virheiden määrä rajataan. Sumeutus (*fuzzing*) satunnaisilla
  syötteillä löytää kääntäjän kaatumiset tehokkaasti (luku 17).
- **Testaa virheilmoitukset.** Virheohjelmat ja niiden odotetut
  tulosteet ovat osa testisarjaa, kuten tässä tutoriaalissa.

## Itsearviointi

- Osaat toteuttaa paniikkitilan toipumisen ja valita sille
  synkronointikohdat kieliopista.
- Osaat selittää, miksi puuttuvan puolipisteen virhe raportoidaan
  seuraavan tokenin kohdalla ja miten sijaintia voi parantaa.
- Osaat nimetä seurannaisvirheiden syitä ja keinoja niitä vastaan.
- Osaat suojata rekursiivisen jäsentimen liian syvältä syötteeltä.
