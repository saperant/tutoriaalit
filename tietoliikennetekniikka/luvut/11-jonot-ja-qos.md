# Jonot ja palvelun laatu

Pakettiverkossa jokaisella linkillä on jono. Kun paketteja saapuu
nopeammin kuin linkki ehtii lähettää, ne odottavat, ja kun jono on
täynnä, ne pudotetaan. Jonoteoria kertoo, miten viive riippuu
kuormasta, ja palvelun laadun (*quality of service*, QoS) mekanismit
päättävät, kuka odottaa.

## M/M/1-jono

Yksinkertaisin jonomalli on M/M/1: paketit saapuvat satunnaisesti
(Poisson-prosessi, keskimäärin $\lambda$ sekunnissa), niiden
palveluajat ovat satunnaisia (eksponentiaalinen, keskimäärin $1/\mu$)
ja palvelijoita on yksi. Kuormitus on $\rho = \lambda / \mu$. Malli
antaa keskimääräiseksi ajaksi järjestelmässä $W = 1/(\mu - \lambda)$
ja keskimääräiseksi määräksi $L = \rho / (1 - \rho)$.

Kaavoja kannattaa uskoa vasta, kun simulaatio vahvistaa ne. Jonon
odotusajat saadaan Lindleyn rekursiolla: seuraavan asiakkaan
odotus on edellisen odotus ja palveluaika miinus saapumisten väli,
kuitenkin vähintään nolla.

```{.python tiedosto="esimerkit/11-mm1.py" osa="lindley"}
```

```{.python tiedosto="esimerkit/11-mm1.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/11-mm1.odotettu"}
```

Tärkein tulos on tekijä $1/(1-\rho)$: kun kuormitus nousee 50 %:sta
90 %:iin, viive viisinkertaistuu, ja 99 %:ssa se on satakertainen.
Jono, jonka kapasiteetti riittää keskimäärin, kasvaa silti pitkäksi,
koska saapumiset ja palveluajat vaihtelevat. Viimeinen sarake
vahvistaa **Littlen lain** $L = \lambda W$, joka pätee mihin tahansa
vakaaseen jonoon jakaumista riippumatta: keskimääräinen määrä
järjestelmässä on saapumisnopeus kertaa keskimääräinen viipymä. Sillä
voi päätellä esimerkiksi tarvittavan säiepoolin koon tai puskurin
koon mitatuista luvuista.

## Prioriteetit

Puhe ja video kestävät vain vähän viivettä, tiedostonsiirto paljon.
Kun samalla linkillä kulkee molempia, prioriteettijono palvelee aina
ensin korkeamman luokan paketit:

```{.python tiedosto="esimerkit/11-prioriteetti.py" osa="jono"}
```

```{.tuloste tiedosto="esimerkit/11-prioriteetti.odotettu"}
```

Kun linkin kuormitus on 85 %, puheen viive on FIFO-jonossa yhtä suuri
kuin datan. Prioriteetilla puheen viive putoaa yhteen millisekuntiin,
eikä datan viive juuri kasva, koska puhe vie vain pienen osan
kapasiteetista. Puhtaan prioriteetin vaara on nälkiintyminen: jos
korkean luokan liikennettä on liikaa, matala luokka ei pääse koskaan
läpi. Siksi korkean luokan liikenne rajataan, ja muut luokat jaetaan
painotetulla reilulla jonotuksella (WFQ, DRR).

## Liikenteen rajoitus: rahakkeen ämpäri

Verkon reunalla rajataan, paljonko liikennettä kukin lähettäjä saa
syöttää. **Rahakkeen ämpäri** (*token bucket*) täyttyy rahakkeilla
sovitulla nopeudella, ja paketti saa mennä vain, jos ämpärissä on sen
kokoinen määrä rahakkeita. Ämpärin koko sallii lyhyet purskeet, mutta
pitkän ajan keskinopeus ei ylitä sovittua:

```{.python tiedosto="esimerkit/11-token-bucket.py" osa="ampari"}
```

```{.python tiedosto="esimerkit/11-token-bucket.py" osa="liikenne"}
```

```{.tuloste tiedosto="esimerkit/11-token-bucket.odotettu"}
```

Purskeen kymmenen ensimmäistä pakettia mahtuvat ämpäriin, loput
hylätään. Sovitun nopeuden alittava tasainen virta menee kokonaan
läpi. Sama algoritmi on operaattorin liittymän nopeusrajoituksessa,
Linuxin `tc`-liikenteenmuokkauksessa ja rajapintojen pyyntörajoissa
(taito *Palveluarkkitehtuurit*). Ylimenevät paketit voidaan pudottaa,
viivästää jonoon (muokkaus, *shaping*) tai merkitä alempaan luokkaan.

## Palvelun laatu verkossa

Internetissä luokat merkitään IP-otsakkeen DSCP-kenttään (DiffServ).
Verkon laitteet sijoittavat paketit luokan mukaan jonoihin; tyypillisiä
luokkia ovat kiireellinen välitys puheelle (EF), varmistettu välitys
liiketoimintadatalle (AF) ja best-effort kaikelle muulle. QoS toimii
vain verkossa, jonka hallitset: julkisessa Internetissä merkintöjä ei
yleensä noudateta. Langattomassa ja matkaviestinverkossa vastaavat
mekanismit ovat Wi-Fin WMM-luokat ja 5G:n QoS-virrat.

## Käytännössä

- **Pidä kuormitus kaukana 100 %:sta.** Viive kasvaa jyrkästi jo
  80–90 %:n kuormituksessa. Mitoita linkit ja palvelimet huipun mukaan
  ja seuraa jonojen pituutta, ei vain keskimääräistä käyttöastetta.
- **Käytä Littlen lakia arviointiin.** Kun tiedät pyyntönopeuden ja
  vasteajan, tiedät, montako pyyntöä on käsittelyssä samanaikaisesti,
  ja siten tarvittavat yhteydet, säikeet ja muistin.
- **Priorisoi vain vähän liikennettä.** Prioriteetti auttaa, kun
  korkean luokan osuus on pieni ja rajattu. Jos kaikki on tärkeää,
  mikään ei ole.
- **Rajoita reunalla, älä keskellä.** Nopeusrajoitus ja luokittelu
  tehdään sisääntulossa, jolloin ydinverkon jonot pysyvät lyhyinä.

## Itsearviointi

- Osaat laskea M/M/1-jonon viiveen ja jonon pituuden kuormituksesta ja
  selittää, miksi viive kasvaa jyrkästi lähellä täyttä kuormaa.
- Osaat simuloida jonon Lindleyn rekursiolla ja verrata tulosta
  kaavaan.
- Osaat soveltaa Littlen lakia järjestelmän mitoitukseen.
- Osaat selittää prioriteettijonon, painotetun jonotuksen ja
  rahakkeen ämpärin toiminnan ja käyttökohteet.
