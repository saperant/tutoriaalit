# Muistin takaisinotto

Lukottomasta rakenteesta poistettua solmua ei voi vapauttaa heti, koska
toinen säie on ehkä juuri lukemassa sitä: se luki osoittimen ennen
poistoa ja seuraa sitä vasta nyt. Lukolla suojatussa rakenteessa ongelmaa
ei ole, koska poisto ja luku eivät ole yhtä aikaa käynnissä. Roskienkeruun
kielissä keräin ratkaisee asian. C++:ssa vapautus on suunniteltava. Tämä
luku käy läpi kolme menetelmää: vaaraosoittimet, epookkipohjaisen
takaisinoton ja viittauslaskennan.

## Vaaraosoittimet

Maged Michaelin vaaraosoittimissa (*hazard pointers*, 2004) jokainen säie
ilmoittaa julkisessa paikassa, mitä solmua se on lukemassa. Poistaja ei
vapauta solmua, jos jokin ilmoitus osoittaa siihen, vaan siirtää sen
odotuslistalle ja yrittää myöhemmin uudelleen:

```{.cpp tiedosto="esimerkit/09-vaaraosoittimet.cpp" osa="pino"}
```

Protokollan ydin on **ilmoita ja vahvista**: säie kirjoittaa
vaaraosoittimen ja lukee pään *uudelleen*. Jos pää on yhä sama, solmu oli
pinossa ilmoituksen jälkeen, joten jokainen sen myöhemmin poistava säie
näkee ilmoituksen. Tämä edellyttää, että ilmoituksen kirjoitus ja pään
uusi luku eivät vaihda järjestystä, eli juuri sitä store buffering
-tilannetta, jonka vain `seq_cst` kieltää (luku *Muistimalli*). Siksi
esimerkki käyttää oletusjärjestystä.

```{.cpp tiedosto="esimerkit/09-vaaraosoittimet.cpp" osa="vapautus"}
```

Odotuslista käsitellään erissä: vasta kun siinä on kaksi kertaa niin monta
solmua kuin vaaraosoittimia, säie lukee kaikki ilmoitukset ja vapauttaa
solmut, joihin mikään ei osoita. Näin vapautusten määrä on
amortisoidusti vakio solmua kohden ja vapauttamatta jää enintään
rajattu määrä solmuja.

```{.cpp tiedosto="esimerkit/09-vaaraosoittimet.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/09-vaaraosoittimet.odotettu"}
```

AddressSanitizer on tässä hyvä testi: jos protokollassa olisi aukko, jokin
säie lukisi vapautettua solmua, ja ajo kaatuisi raporttiin
`heap-use-after-free`. Kierrätys ei myöskään tuota ABA-ongelmaa, koska
solmu, johon joku osoittaa, ei vapaudu eikä sen osoite voi palata
pinoon uutena solmuna.

Esimerkki on yksinkertaistettu: säikeiden määrä on kiinteä, ja jokainen
säie saa numeronsa kutsussa. Tuotantototeutukset (Folly, C++26:n
`std::hazard_pointer`) varaavat paikat dynaamisesti ja käsittelevät myös
säikeen päättymisen.

## Epookkipohjainen takaisinotto

Vaaraosoitin maksaa jokaisella luvulla `seq_cst`-kirjoituksen ja uuden
luvun. **Epookkipohjainen takaisinotto** (*epoch-based reclamation*,
Fraser 2004) on lukijalle halvempi:

1. Ohjelmassa on globaali epookkilaskuri. Lukija ilmoittaa aloittaessaan
   näkemänsä epookin ja lopettaessaan olevansa ulkona.
2. Poistettu solmu merkitään sen hetken epookilla.
3. Epookki voi kasvaa vain, kun kaikki aktiiviset lukijat ovat nähneet
   nykyisen epookin. Kun epookki on kasvanut kahdesti solmun
   poistamisen jälkeen, kukaan ei voi enää viitata siihen, ja se
   vapautetaan.

Lukija maksaa kaksi kirjoitusta lukujakson alussa ja lopussa, ei yhtään
osoitinta kohden. Haittapuoli on, että yksikin jumittunut tai hidas lukija
pysäyttää kaiken vapauttamisen, joten muisti voi kasvaa rajatta.
Vaaraosoittimet rajaavat vapauttamattomat solmut aina. Crossbeam
(Rust) ja monet tietokantamoottorit käyttävät epookkeja.

**RCU** (*read-copy-update*) on Linuxin ytimen vastaava menetelmä, jossa
lukija ei kirjoita mitään: ydin tietää, että lukijat eivät nuku
lukujaksossa, joten jokaisen ytimen kontekstinvaihto todistaa lukijoiden
poistuneen. Käyttäjätilassa sitä tarjoaa liburcu, ja C++26 standardoi
`std::rcu_obj_base`n ja funktion `std::rcu_synchronize`.

## Viittauslaskenta

Yksinkertaisin turvallinen ratkaisu on viittauslaskenta: olio vapautuu,
kun viimeinen viittaus katoaa. `std::atomic<std::shared_ptr<T>>` (C++20)
sallii jaetun osoittimen lukemisen ja vaihtamisen atomisesti. Sen päälle
rakentuu **kopioi ja vaihda** -malli (*copy-on-write*): lukija ottaa
muuttumattoman tilannekuvan, ja kirjoittaja tekee kopion, muuttaa sitä ja
vaihtaa sen paikalleen:

```{.cpp tiedosto="esimerkit/09-jaettu-osoitin.cpp" osa="reititys"}
```

```{.cpp tiedosto="esimerkit/09-jaettu-osoitin.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/09-jaettu-osoitin.odotettu"}
```

Lukija ei koskaan näe puolivalmista tilaa, koska kukaan ei muuta
julkaistua oliota. Vanha versio elää niin kauan kuin joku lukija pitää
sitä, ja vapautuu viimeisen mukana. Kahden kirjoittajan kilpailu
ratkaistaan CAS:lla: jos joku muu ehti vaihtaa version, kopio tehdään
uudelleen uusimmasta. Malli sopii asetuksiin, reititystauluihin ja muuhun
dataan, joka luetaan usein ja muuttuu harvoin.

`std::atomic<std::shared_ptr>` ei ole libstdc++:ssa lukoton
(`is_lock_free()` palauttaa `false`): toteutus käyttää lyhyttä
sisäistä lukkoa viittauslaskurin päivityksen ajan. Lisäksi jokainen
lukeminen kasvattaa yhteistä viittauslaskuria, joka on kilpailtu
välimuistirivi. Erittäin luetussa datassa vaaraosoittimet tai RCU
skaalautuvat paremmin.

## Vertailu

| Menetelmä | Lukijan hinta | Vapauttamatta jäävä muisti | Haitta |
|-----------|---------------|-------------|-----------|
| Ei vapautusta ajon aikana | Ei mitään | Kaikki | Vain lyhyisiin ajoihin |
| Vaaraosoittimet | `seq_cst`-kirjoitus ja uusi luku osoitinta kohden | Rajattu | Monimutkainen |
| Epookit | Kaksi kirjoitusta lukujaksoa kohden | Rajaton, jos lukija jumittuu | Hidas lukija estää vapautuksen |
| RCU (ydin) | Ei mitään | Kunnes kaikki ytimet ovat vaihtaneet kontekstia | Vaatii ytimen tai kirjaston tuen |
| `atomic<shared_ptr>` | Viittauslaskurin päivitys | Ei mitään | Kilpailtu laskuri, ei lukoton |

## Käytännössä

- **Takaisinotto kuuluu suunnitteluun.** Lukottoman rakenteen
  toteutus ei ole valmis ennen kuin on päätetty, milloin solmut
  vapautetaan. Useimmat julkaistut algoritmit olettavat roskienkeruun.
- **Kopioi ja vaihda ensin.** Harvoin muuttuvalle datalle
  `atomic<shared_ptr<const T>>` on yksinkertaisin oikea ratkaisu. Lukija
  saa eheän tilannekuvan, jota se voi pitää niin kauan kuin tarvitsee.
- **Muuttumattomuus helpottaa.** Julkaistua oliota ei muuteta; muutos on
  aina uusi versio. Tällöin lukijoiden ja kirjoittajan välillä ei ole
  datakilpailuja.
- **Käytä valmiita toteutuksia.** Folly, liburcu ja C++26:n
  `std::hazard_pointer` ja `std::rcu` ovat tarkasti testattuja.
- **AddressSanitizer stressitestiin.** Takaisinoton virheet näkyvät
  vapautetun muistin käyttönä, jonka ASan löytää, kun virheellinen
  lomitus osuu kohdalle.

## Itsearviointi

- Osaat selittää, miksi poistettua solmua ei voi vapauttaa heti
  lukottomassa rakenteessa.
- Osaat toteuttaa vaaraosoitinprotokollan ja perustella, miksi
  ilmoituksen ja vahvistuksen on oltava `seq_cst`.
- Osaat kuvata epookkipohjaisen takaisinoton ja RCU:n periaatteen ja
  niiden heikkoudet.
- Osaat käyttää `std::atomic<std::shared_ptr>`ia kopioi ja vaihda
  -mallissa ja arvioida sen hinnan.
