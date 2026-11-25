# Luokat ja oliot

Tähän asti data ja sitä käsittelevät funktiot ovat olleet erillään.
Kun ohjelma kasvaa, on hyödyllistä koota yhteen asiaan liittyvä data ja
sitä koskevat säännöt. *Luokka* on oma tyyppi, joka määrittelee,
millaista dataa sen *olioilla* on ja mitä niillä voi tehdä. Pythonin
`str` ja `list` ovat luokkia; `"abc"` on `str`-luokan olio, ja `upper`
on sen *metodi*.

## Luokka ja invariantti

Pankkitilillä on omistaja ja saldo. Saldo ei saa koskaan olla
negatiivinen. Tällainen aina voimassa oleva sääntö on luokan
*invariantti*. Luokka valvoo sitä niin, että saldoa muutetaan vain
metodeilla, jotka tarkistavat säännön:

```{.python tiedosto="esimerkit/08-tili.py"}
```

```{.tuloste tiedosto="esimerkit/08-tili.odotettu"}
```

- `class Tili:` määrittelee luokan. Luokkien nimet kirjoitetaan isolla
  alkukirjaimella ilman alaviivoja (`KateEiRiita`).
- `__init__` on *konstruktori*, joka suoritetaan, kun olio luodaan
  kutsulla `Tili("Aino", 5000)`. Se asettaa olion *attribuutit*.
- `self` on olio itse. `self.omistaja` on tämän olion omistaja; jokaisella
  tilillä on omat attribuuttinsa.
- Alaviivalla alkava nimi `_saldo` on sopimus: attribuutti on luokan
  sisäinen, eikä sitä muuteta luokan ulkopuolelta. `@property` antaa
  lukea saldon nimellä `aino.saldo` muttei sijoittaa siihen.
  Määrittelyn yläpuolelle kirjoitettu `@nimi` on *dekoraattori*: se
  muuttaa heti alla määritellyn funktion tai luokan toimintaa.
- `__str__` määrää, miltä olio näyttää tulostettuna.
- `KateEiRiita` on oma poikkeusluokka. Se *periytyy* luokasta
  `Exception`, eli se on poikkeus, ja kutsuja voi siepata juuri sen.
  Oma tyyppi kertoo virheen lajin tarkemmin kuin yleinen `ValueError`.

Koska kaikki muutokset kulkevat metodien kautta, invariantti pätee
jokaisen metodikutsun jälkeen. Jos saldoa voisi muuttaa suoraan,
jokaisen saldoa muuttavan kohdan pitäisi muistaa tarkistus.

## Dataluokat ja koostaminen

Moni luokka on lähinnä nimetty kokoelma kenttiä. Dekoraattori
`@dataclass` kirjoittaa tällaiselle luokalle konstruktorin, tulostusmuodon
ja vertailun automaattisesti kenttien tyyppivihjeiden perusteella:

```{.python tiedosto="esimerkit/08-ostoskori.py"}
```

```{.tuloste tiedosto="esimerkit/08-ostoskori.odotettu"}
```

```{.dot otsikko="Esimerkin oliot lopussa: kori viittaa riveihin ja jokainen rivi tuotteeseensa."}
digraph {
  rankdir=LR; nodesep=0.25; ranksep=0.5;
  kori [label="Ostoskori\nrivit"];
  r1 [label="Rivi\nmaara = 1"];
  r2 [label="Rivi\nmaara = 6"];
  t1 [label="Tuote\nnimi = \"Kahvi 500 g\"\nhinta_snt = 699"];
  t2 [label="Tuote\nnimi = \"Korvapuusti\"\nhinta_snt = 150"];
  kori -> r1 [label="rivit[0]"];
  kori -> r2 [label="rivit[1]"];
  r1 -> t1 [label="tuote"];
  r2 -> t2 [label="tuote"];
}
```

Ostoskori *koostuu* riveistä, ja rivi koostuu tuotteesta ja määrästä.
Jokainen luokka vastaa omasta osastaan: rivi osaa laskea oman hintansa,
kori koko summan. *Koostaminen* (olio sisältää toisia olioita) on
tavallisin tapa rakentaa isompia kokonaisuuksia pienistä.

`field(default_factory=list)` antaa jokaiselle korille oman tyhjän
listan. Pelkkä `rivit: list[Rivi] = []` ei ole sallittu, koska kaikki
korit jakaisivat silloin saman listan (vrt. luvun *Kokoelmat*
viittaukset).

## Periytyminen

Luokka voi *periä* toisen luokan: `class Saastotili(Tili):` saa kaikki
`Tili`-luokan attribuutit ja metodit ja voi lisätä omiaan tai
korvata niitä. Periytyminen sopii, kun uusi luokka todella on
erikoistapaus yläluokasta ja sitä voi käyttää kaikkialla, missä
yläluokkaakin. Perusteissa sitä tarvitaan lähinnä omissa
poikkeusluokissa; muuten koostaminen on yleensä parempi valinta.
Taito *Python* käsittelee periytymisen, rajapinnat ja protokollat.

## Kokeile itse

Tarkistin luo luokasta olioita, kutsuu niiden metodeja ja vertaa
tulosta. Tehtävänannon nimet (luokka, metodit ja attribuutit) on
siksi kirjoitettava täsmälleen samoin.

1. **Laskuri** (`08-1`). Luokka `Laskuri`, jolla on metodit `kasvata`
   ja `nollaa` sekä attribuutti `arvo`.
2. **Suorakulmio dataluokkana** (`08-2`). Dataluokka `Suorakulmio`,
   jolla on kentät `leveys` ja `korkeus` ja metodit `pinta_ala` ja
   `on_nelio`.
3. **Varasto ja invariantti** (`08-3`). Luokka `Varasto`, jonka määrä
   pysyy välillä 0–kapasiteetti. Sääntöä rikkova kutsu nostaa oman
   poikkeuksen `VarastoVirhe` eikä muuta tilaa.

## Käytännössä

- **Luokka, kun data ja sen säännöt kuuluvat yhteen.** Tili, jonka
  saldo ei saa mennä negatiiviseksi, on luokka. Pelkkä laskenta ilman
  tilaa on funktio; luokka, jolla on vain yksi metodi, on yleensä
  tarpeeton.
- **Invariantti konstruktorissa ja metodeissa.** Olio ei saa koskaan
  olla virheellisessä tilassa. Tarkista arvot `__init__`issä ja
  jokaisessa muuttavassa metodissa ja nosta poikkeus, jos sääntö
  rikkoutuisi.
- **Kapselointi:** muuta tilaa metodeilla, ei kirjoittamalla
  attribuutteihin luokan ulkopuolelta. Alaviiva merkitsee sisäisen
  attribuutin.
- **Dataluokka datalle.** Kun luokka on pääasiassa joukko nimettyjä
  kenttiä, `@dataclass` säästää toistuvalta koodilta ja virheiltä.
  Nimetyt kentät ovat selvempiä kuin monikon `tuote[1]`.
- **Koostaminen ennen periytymistä** (*composition over
  inheritance*). Syvät periytymishierarkiat sitovat luokat tiukasti
  toisiinsa; koostaminen pitää osat erillisinä ja vaihdettavina.
- **Oma poikkeusluokka**, kun kutsujan pitää pystyä erottamaan tämä
  virhe muista.

## Itsearviointi

- Osaat määritellä luokan, jolla on konstruktori, attribuutteja ja
  metodeja, ja luoda siitä olioita.
- Osaat nimetä luokan invariantin ja valvoa sitä metodeissa.
- Osaat kirjoittaa dataluokan ja koota luokista suuremman
  kokonaisuuden.
- Osaat määritellä oman poikkeusluokan ja perustella sen käytön.
- Osaat perustella, milloin ongelma ratkaistaan luokalla ja milloin
  pelkillä funktioilla.
