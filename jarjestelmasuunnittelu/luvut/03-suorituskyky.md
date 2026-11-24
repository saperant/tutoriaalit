# Suorituskyky ja skaalautuvuus

Suorituskyvyllä on kaksi ulottuvuutta. *Latenssi* (vasteaika) on se,
kuinka kauan yksi pyyntö kestää. *Läpäisy* (*throughput*) on se, kuinka
monta pyyntöä järjestelmä käsittelee aikayksikössä. Ne ovat eri asioita:
kapasiteetin lisääminen nostaa läpäisyä mutta ei nopeuta yksittäistä
pyyntöä, ja kuorman kasvaessa latenssi kasvaa jo kauan ennen kuin
läpäisy on huipussaan. *Skaalautuvuus* tarkoittaa, että läpäisy kasvaa
resursseja lisäämällä ilman, että latenssi kärsii.

## Persentiilit ja häntälatenssi

Latenssi ei ole yksi luku vaan jakauma. Keskiarvo kätkee juuri sen, mikä
käyttäjälle on pahinta: harvinaiset hitaat pyynnöt. Siksi latenssi
ilmoitetaan persentiileinä: p50 (mediaani) on tyypillinen pyyntö, p99
on raja, jonka alle 99 % pyynnöistä jää, ja p99,9 kertoo hännästä.
Hitaat pyynnöt eivät ole harvinaisia käyttäjälle: sivu, joka tekee
sata taustakutsua, osuu lähes aina johonkin hitaaseen.

Esimerkissä taustapalvelu vastaa yleensä 5–15 ms:ssa, mutta 1 % kutsuista
kestää 100–300 ms (roskienkeruu, levyn hetkellinen ruuhka, naapurin
kuorma samassa virtuaalikoneessa). Pyyntö, joka kysyy *n* palvelinta
rinnakkain ja odottaa kaikkia, on yhtä hidas kuin hitain vastaus:

```{.python tiedosto="esimerkit/luku03/hantalatenssi.py" osa="kutsu"}
```

```{.tuloste tiedosto="esimerkit/luku03/hantalatenssi.odotettu"}
```

Yhden kutsun p99 on 105 ms. Kymmenen kutsun pyynnön mediaani on vielä
14 ms, mutta p99 on 280 ms, lähellä hitaimman mahdollisen kutsun kestoa.
Sadan kutsun pyynnön mediaani on 160 ms: 63 % pyynnöistä osuu ainakin
yhteen hitaaseen kutsuun, joten tyypillinen pyyntö on hidas. Ilmiö tunnetaan nimellä
*tail at scale*: mitä laajemmin pyyntö hajautuu, sitä enemmän häntä
ratkaisee.

Varmistettu pyyntö (*hedged request*) lähettää saman kyselyn toiselle
kopiolle, jos ensimmäinen ei vastaa tietyn ajan kuluessa. Raja asetetaan
lähelle p95:tä, jolloin lisäkutsuja tulee muutama prosentti. Tulos on
dramaattinen: kymmenen kutsun p99 putoaa 280 ms:sta 34 ms:iin. Ehto on,
että kysely on idempotentti ja että hitaus on satunnaista eikä
kuormasta johtuvaa; ylikuormitetulle palvelulle lisäkutsut ovat haitaksi
(luku 9).

## Littlen laki ja käyttöaste

Littlen laki yhdistää kolme suuretta mitä tahansa vakaata järjestelmää
varten: järjestelmässä olevien pyyntöjen määrä *L* on saapumisnopeus λ
kertaa keskimääräinen viipymäaika *W*:

$$L = \lambda W$$

Jos palvelu saa 2 400 pyyntöä sekunnissa ja jokainen viipyy 20 ms, kesken
on keskimäärin 48 pyyntöä. Laki ei oleta mitään jakaumista, ja sillä
mitoitetaan säieallas, tietokannan yhteysallas ja jonon pituus.

Jonoteoria kertoo, mitä tapahtuu käyttöasteen kasvaessa: kun palvelin on
varattuna osuuden ρ ajasta, jonotusaika kasvaa kuin 1/(1 − ρ). Malleja
käsitellään syvemmin taidossa *Arkkitehtuurin mallinnus ja
suunnittelutilan tutkiminen*; tässä niitä käytetään mitoitukseen.
M/M/c-mallin Erlangin C-kaava antaa todennäköisyyden, että pyyntö joutuu
odottamaan, kun rinnakkaisia käsittelijöitä on *c*:

```{.python tiedosto="esimerkit/luku03/kapasiteetti.py" osa="erlang"}
```

```{.tuloste tiedosto="esimerkit/luku03/kapasiteetti.odotettu"}
```

Kuusi palvelinta riittää keskimäärin juuri ja juuri, mutta käyttöaste
100 % tarkoittaa rajatonta jonoa. Seitsemällä palvelimella 19 %
pyynnöistä joutuu odottamaan. Tulos näyttää myös *yhdistämisen edun*: kun
yhteisessä altaassa on 56 käsittelijää, 86 % käyttöaste on vielä
kohtuullinen (jonotus 0,47 ms), kun taas yhdellä käsittelijällä
keskimääräinen jonotus olisi kuusinkertainen palveluaikaan nähden. Siksi yksi suuri jono useamman palvelimen
edessä on parempi kuin erillinen jono kullekin, kunhan kuormantasaaja
jakaa työn hyvin (luku 4).

Viimeinen rivi on tavallinen mitoitussääntö: kapasiteetin on riitettävä
myös silloin, kun yksi palvelin on poissa (N + 1), ja käyttöasteen on
jäätävä silloinkin turvalliselle tasolle. Kymmenen palvelinta on 60 %
käyttöaste normaalisti ja 67 % yhden puuttuessa.

## Pysty- ja vaakaskaalaus

*Pystyskaalaus* (*scale up*) tarkoittaa isompaa konetta: enemmän ytimiä,
muistia ja nopeampi levy. Se on yksinkertaisinta, koska ohjelma ei
muutu, ja nykyiset palvelimet ovat suuria. Rajat ovat hinta (suurimmat
koneet maksavat suhteessa enemmän), yksi vikaantumispiste ja se, että
suurin kone on lopulta liian pieni.

*Vaakaskaalaus* (*scale out*) tarkoittaa lisää samanlaisia koneita.
Se vaatii, että työ jakautuu:

- **Tilaton sovelluskerros.** Pyyntö ei saa riippua siitä, mikä
  palvelin edellisen pyynnön käsitteli. Istunto, ostoskori ja
  välitulokset tallennetaan jaettuun tallennukseen (Redis, tietokanta)
  tai asiakkaalle (allekirjoitettu evästeen sisältö). Silloin mikä
  tahansa palvelin kelpaa, palvelimen voi kaataa tai lisätä milloin
  tahansa, ja kuormantasaus on yksinkertaista.
- **Tilallinen kerros jaetaan erikseen.** Tietokanta ja välimuisti
  skaalautuvat replikoinnilla (lisää lukukapasiteettia, luku 7) ja
  osioinnilla (lisää kirjoitus- ja tallennuskapasiteettia, luku 5).

Skaalautuvuutta rajoittaa jaettu osa. Amdahlin laki pätee
järjestelmiinkin: jos jokainen pyyntö kulkee saman tietokantarivin tai
lukon kautta, palvelimien lisääminen ei auta. Lisäksi koordinaatio
maksaa: Gunther kuvasi universaalissa skaalautuvuuslaissa (USL)
termin, joka kasvaa solmujen määrän neliönä, ja silloin läpäisy voi
jopa laskea solmuja lisättäessä. Käytännössä kysytään: mitä jokainen
pyyntö jakaa kaikkien muiden kanssa?

## Käytännössä

- **Aseta latenssitavoite persentiilinä.** "p99 alle 200 ms" on
  mitattava ja testattava, "nopea" ei. Mittaa persentiilit oikein:
  histogrammeista, ei keskiarvoista (luku 11).
- **Pidä hajautetut pyynnöt kapeina.** Jokainen rinnakkainen kutsu
  heikentää häntää. Kokoa data valmiiksi (denormalisointi, esilaskenta),
  jos lukupolku muuten hajautuisi kymmeniin palveluihin.
- **Käytä varmistettuja pyyntöjä varoen.** Ne leikkaavat hännän, kun
  hitaus on satunnaista, mutta kuormittavat lisää, kun hitaus johtuu
  ylikuormasta. Rajaa niiden osuus.
- **Mitoita käyttöasteelle 60–70 % yhden palvelimen puuttuessa.** Jono
  kasvaa jyrkästi käyttöasteen lähestyessä sataa, ja kuorman vaihtelu
  vie keskiarvon yli rajan.
- **Tee sovelluskerroksesta tilaton.** Se on vaakaskaalauksen,
  automaattisen skaalauksen ja kaatumisista toipumisen edellytys.

## Itsearviointi

- Osaat selittää latenssin ja läpäisyn eron ja sen, miksi latenssi
  ilmoitetaan persentiileinä.
- Osaat laskea, kuinka hajautettu pyyntö vahvistaa häntälatenssia, ja
  kertoa varmistetun pyynnön hyödyn ja hinnan.
- Osaat käyttää Littlen lakia ja jonomallia palvelinmäärän ja
  allaskokojen mitoitukseen N + 1 -periaatteella.
- Osaat perustella, miksi tilaton sovelluskerros skaalautuu vaakaan ja
  mikä jaettu osa rajoittaa skaalautuvuutta.
