# Kustannukset ja kapasiteetti

Ylläpitäjän päätökset ovat myös rahapäätöksiä. Hankitaanko palvelimet
vai vuokrataanko kapasiteetti pilvestä, milloin levyjä on tilattava ja
paljonko varakapasiteettia kannattaa pitää? Vastaukset perustuvat
laskelmiin, joiden oletukset kirjoitetaan auki, jotta ne voi tarkistaa
ja päivittää.

## Kokonaiskustannukset (TCO)

Palvelimen hankintahinta on usein alle kolmannes sen kustannuksista
käyttöiän aikana. Kokonaiskustannuksiin (total cost of ownership)
lasketaan:

- **Laitteet** ja niiden vaihto käyttöiän lopussa (tyypillisesti
  5 vuotta).
- **Sähkö ja jäähdytys.** Konesalin tehokkuutta kuvaa PUE (power
  usage effectiveness): kokonaisenergia jaettuna IT-laitteiden
  energialla. PUE 1,5 tarkoittaa, että jäähdytys ja muu infrastruktuuri
  kuluttavat puolet IT-laitteiden kulutuksesta.
- **Tila ja verkko**: räkkitila, sähkösyötöt, yhteydet.
- **Tuki ja lisenssit**: huoltosopimukset, virtualisoinnin ja
  käyttöjärjestelmien lisenssit.
- **Työ**: asennus, päivitykset, vianselvitys, hankinnat.

```{.python tiedosto="esimerkit/11-tco.py" osa="tco"}
```

```{.python tiedosto="esimerkit/11-tco.py" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/11-tco.odotettu"}
```

Tulos riippuu ennen kaikkea käyttöasteesta. Jatkuvasti päällä oleva
kuorma on omassa konesalissa halvempi kuin pilvessä listahinnoin,
mutta kolmen vuoden sitoumuksella tai kun kuorma skaalautuu tarpeen
mukaan, pilvi on halvempi. Ylläpitotyö on molemmissa merkittävä erä,
ja pilven etu tulee osin siitä, että laitteiston, konesalin ja
virtualisoinnin ylläpito siirtyy palveluntarjoajalle. Laskelma ei
sisällä riskejä ja joustavuutta: pilvessä kapasiteettia saa minuuteissa,
omaan konesaliin viikoissa.

## Kapasiteetin ennustaminen

Kapasiteetin loppuminen on harvoin yllätys, jos käyttöä seurataan.
Kasvusta sovitetaan malli, ja siitä lasketaan, milloin raja ylittyy.
Hankinta on aloitettava hankinta-ajan verran aiemmin:

```{.python tiedosto="esimerkit/11-kapasiteetti.py" osa="ennuste"}
```

```{.tuloste tiedosto="esimerkit/11-kapasiteetti.odotettu"}
```

Käyttö on nyt 68 %, eikä mitään hälytystä ole lauennut, mutta
laajennus on tilattava neljän kuukauden kuluessa. Raja 80 % jättää
varaa uudelleenrakennuksille, tilannevedoksille ja kasvun
kiihtymiselle; levyjärjestelmät myös hidastuvat lähes täysinä.

Lineaarinen malli sopii tasaiseen kasvuun. Kausivaihtelu (joulumyynti,
kuukauden vaihteen ajot) ja kertaluonteiset muutokset (uusi asiakas,
datan siirto) huomioidaan erikseen, ja ennuste päivitetään
kuukausittain.

## Varakapasiteetti

Varakapasiteetti on vakuutus, jolla on hinta. Sen määrää kolme asiaa:

1. **Vikasietoisuus.** N+1 vaatii klusterissa yhden ylimääräisen
   isännän (luku *Virtualisointialustat ja klusterit*), RAID 6 kaksi
   ylimääräistä levyä.
2. **Kuormapiikit.** Palvelun on kestettävä huippukuorma, ei
   keskimääräistä.
3. **Hankinta-aika.** Mitä pidempi toimitus, sitä enemmän puskuria.
   Pilvessä hankinta-aika on lähes nolla, joten varakapasiteettia
   tarvitaan vähemmän.

Kun varakapasiteetti on mitoitettu näin perustein, se ei ole
tuhlausta: jokaiselle ylimääräiselle palvelimelle on tehtävä.

## Käytännössä

- **Laske TCO, älä hankintahintaa.** Sähkö, tila, tuki ja työ mukaan,
  ja oletukset näkyviin.
- **Vertaa käyttöasteella.** Jatkuva kuorma ja vaihteleva kuorma
  johtavat eri ratkaisuun.
- **Ennusta kuukausittain** ja hälytä ennusteesta ("tila loppuu
  kuuden kuukauden päästä"), ei vain nykyisestä täyttöasteesta.
- **Mitoita vara perustein**: vikasietoisuus, piikit ja hankinta-aika.
- **Seuraa kustannuksia palveluittain.** Tunnisteet (tagit) pilvessä
  ja kustannuspaikat omassa konesalissa kertovat, mikä palvelu
  maksaa ja paljonko.

## Itsearviointi

- Osaat koota palvelun kokonaiskustannukset ja selittää PUE:n
  merkityksen.
- Osaat verrata omaa konesalia ja pilveä käyttöasteen ja sitoumusten
  perusteella.
- Osaat ennustaa kapasiteetin loppumisen käyttöhistoriasta ja ajoittaa
  hankinnan.
- Osaat perustella varakapasiteetin määrän vikasietoisuuden, piikkien
  ja hankinta-ajan avulla.
