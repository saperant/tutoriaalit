# Säikeet ja atomiset operaatiot {.runko-rinnakkaisuus}

C11 lisäsi kieleen muistimallin, säikeet (`<threads.h>`) ja atomiset
tyypit (`<stdatomic.h>`). Sitä ennen säikeistys oli
käyttöjärjestelmäkohtaisten rajapintojen, kuten POSIX-säikeiden
(`pthread`), varassa. Standardin säikeet ovat ohut kerros näiden päällä,
ja ne ovat käytettävissä esimerkiksi glibc:ssä, muslissa ja uusissa
Windows-ympäristöissä. POSIX-säikeet ovat edelleen yleisiä, ja niiden
rajapinta on hyvin samankaltainen.

## Säikeen luominen

`thrd_create` käynnistää uuden säikeen, joka suorittaa annetun funktion.
Funktio saa yhden `void *`-argumentin ja palauttaa `int`-arvon.
`thrd_join` odottaa säikeen päättymistä. Jokainen säie on joko odotettava
tai irrotettava (`thrd_detach`), muuten sen resurssit eivät vapaudu.

Seuraava ohjelma laskee summan neljässä säikeessä. Jokainen säie saa
oman `Osa`-rakenteensa ja kirjoittaa tuloksen vain siihen, joten
säikeet eivät käsittele samaa muistia eikä lukitusta tarvita:

```{.c tiedosto="esimerkit/12-saikeet.c" osa="tehtava"}
```

```{.c tiedosto="esimerkit/12-saikeet.c" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/12-saikeet.odotettu"}
```

Esimerkissä taulukon pituus on jaollinen säikeiden määrällä.
Yleisessä tapauksessa viimeinen säie käsittelisi myös jakojäännöksen.
Nimetön `enum` on vanha tapa määritellä kokonaislukuvakioita, joita
voi käyttää taulukon kokona; C23:ssa sama onnistuu `constexpr`:llä.

## Kilpatilanteet ja lukot

Jos kaksi säiettä käsittelee samaa muistipaikkaa samanaikaisesti ja
ainakin toinen kirjoittaa, syntyy *kilpatilanne* (*data race*), joka on
määrittelemätöntä käyttäytymistä. Jopa `saldo += 1` koostuu lukemisesta,
lisäyksestä ja kirjoittamisesta, ja kahden säikeen operaatiot voivat
lomittua niin, että lisäyksiä katoaa. Seuraavassa kumpikin säie lukee
arvon 5 ennen kuin toinen ehtii kirjoittaa, ja kahden lisäyksen jälkeen
saldo on 6 eikä 7:

| Vaihe | Säie A | Säie B | `saldo` |
|-------|--------|--------|---------|
| 1 | lukee 5 | | 5 |
| 2 | | lukee 5 | 5 |
| 3 | laskee 5 + 1 | | 5 |
| 4 | | laskee 5 + 1 | 5 |
| 5 | kirjoittaa 6 | | 6 |
| 6 | | kirjoittaa 6 | 6 |

Jaettu data suojataan *lukolla* (`mtx_t`). `mtx_lock` odottaa, kunnes
lukko on vapaa, ja varaa sen; `mtx_unlock` vapauttaa sen. Lukon sisällä
oleva koodi suoritetaan siis yksi säie kerrallaan. Yksittäisille
laskureille ja lipuille kevyempi vaihtoehto on *atominen* tyyppi, kuten
`atomic_int`, jonka operaatiot ovat jakamattomia:

```{.c tiedosto="esimerkit/12-lukitus.c" osa="jaettu"}
```

```{.c tiedosto="esimerkit/12-lukitus.c" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/12-lukitus.odotettu"}
```

Ilman lukkoa saldo jäisi satunnaisesti alle 40000:n. Jokainen
`mtx_lock`-kutsu on vapautettava täsmälleen kerran kaikilla
suorituspoluilla; C:ssä ei ole C++:n kaltaisia olioita, jotka tekisivät
sen automaattisesti. Kun lukkoja on useita, ne on aina varattava samassa
järjestyksessä, jotta säikeet eivät jää odottamaan toisiaan
(*lukkiutuminen*, *deadlock*).

Lukon kanssa käsitelty muuttuja ei tarvitse `volatile`-määrettä.
`volatile` on tarkoitettu laitteistorekistereille ja vastaaville, eikä
se tee operaatioista atomisia tai säieturvallisia.

## Tuottaja–kuluttaja-jono

Säikeiden välinen työnjako tehdään usein jonon kautta: yksi säie tuottaa
tehtäviä ja muut käsittelevät niitä. Lukon lisäksi tarvitaan
*ehtomuuttujia* (`cnd_t`), joiden avulla säie voi nukkua, kunnes jonoon
tulee tilaa tai tehtäviä.

```{.c tiedosto="esimerkit/12-jono.c" osa="jono"}
```

`cnd_wait` vapauttaa lukon odotuksen ajaksi ja varaa sen uudelleen
herätessään. Ehto tarkistetaan silmukassa, koska herätys voi tulla
ilman, että ehto on tosi. Jonon sulkeminen herättää kaikki kuluttajat,
jotta ne voivat lopettaa, kun jono on tyhjä.

```{.c tiedosto="esimerkit/12-jono.c" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/12-jono.odotettu"}
```

Kuluttajien keskinäinen työnjako vaihtelee ajokerrasta toiseen, mutta
kokonaissumma on aina sama.

## Kilpatilanteiden testaaminen

Kilpatilanteet ilmenevät satunnaisesti, joten testi voi mennä läpi
tuhat kertaa ja epäonnistua tuhannes ensimmäisellä kerralla.
ThreadSanitizer (`-fsanitize=thread`) havaitsee kilpatilanteet ajon
aikana, vaikka ne eivät sillä kertaa aiheuttaisi väärää tulosta.
Tämän luvun esimerkit on kuitenkin testattu vain AddressSanitizerilla
ja UndefinedBehaviorSanitizerilla: ThreadSanitizer ei tue glibc:n
`<threads.h>`-toteutusta, vaan ohjelma kaatuu säikeen luonnissa.
POSIX-säikeitä käyttäville ohjelmille ThreadSanitizer toimii.

## Käytännössä

- **Jaa data, älä tilaa.** Paras synkronointi on se, jota ei tarvita:
  kukin säie käsittelee omaa osaansa, ja tulokset yhdistetään lopuksi
  (luvun ensimmäinen esimerkki).
- **Lukko suojaa dataa, ei koodia.** Jokaisella jaetulla tiedolla on
  yksi lukko, ja se dokumentoidaan rakenteen kenttien viereen. Lukko
  pidetään mahdollisimman lyhyesti, eikä sen sisällä tehdä I/O:ta eikä
  muistinvarauksia.
- **Lukitusjärjestys.** Jos lukkoja on useita, ne varataan aina samassa
  järjestyksessä. Yksi lukko on usein parempi kuin monta.
- **Ehtomuuttuja aina silmukassa** ja jaetun ehdon muutos aina lukon
  alla.
- **Säieturvattomat funktiot.** `strtok`, `rand` ja `localtime` käyttävät
  sisäistä tilaa. Niiden tilalle tulevat `_r`-versiot tai säiekohtainen
  tila (C23:n `thread_local`).
- **Atomiset muuttujat** laskureihin ja lippuihin. Heikommat
  muistijärjestykset (`memory_order_relaxed` ym.) vain, kun tarve on
  mitattu ja mallin tuntee; oletusjärjestys on turvallisin.
- **Tuotannossa** käytetään usein POSIX-säikeitä ja säiepoolia: säikeitä
  ei luoda tehtävää kohti, vaan kiinteä joukko säikeitä lukee tehtäviä
  jonosta kuten yllä.

## Itsearviointi

- Osaat jakaa työn säikeille niin, että kukin käsittelee omaa dataansa.
- Osaat suojata jaetun datan lukolla ja välttää lukkiutumisen.
- Osaat toteuttaa tuottaja–kuluttaja-jonon ehtomuuttujilla.
- Osaat perustella valinnan lukon ja atomisen muuttujan välillä.
