# Muistinvaraajat

Ydin antaa prosessille muistia sivuina: `mmap` tai keon kasvatus
`brk`-kutsulla. Ohjelmat taas varaavat kymmenen tai sata tavua
kerrallaan. Väliin tarvitaan *varaaja*, joka pilkkoo sivut pieniksi
lohkoiksi ja kierrättää vapautetut. Käyttäjätilassa se on C-kirjaston
`malloc`; ytimessä vastaavat työt tekevät sivuvaraaja (buddy
allocator) ja sen päällä slab-varaaja.

Hyvä varaaja on nopea, tuhlaa vähän muistia ja pitää yhdessä
käytetyt oliot lähellä toisiaan. Tuhlausta on kahta lajia:

- **Sisäinen pirstoutuminen:** lohko on suurempi kuin pyydetty,
  esimerkiksi tasauksen tai pienimmän lohkokoon vuoksi.
- **Ulkoinen pirstoutuminen:** vapaata muistia on yhteensä tarpeeksi,
  mutta se on hajallaan liian pieninä paloina.

## Implisiittinen lohkolista

Yksinkertaisin varaaja pitää keon lohkoina, joista kunkin alussa on
*otsake*: lohkon koko ja tieto siitä, onko se vapaa. Seuraava lohko
löytyy lisäämällä koko osoitteeseen, joten lohkot muodostavat listan
ilman erillisiä linkkejä. Otsake on 16 tavua, jotta otsakkeen perässä
oleva hyötykuorma on tasattu kuten `malloc` lupaa:

```{.c tiedosto="esimerkit/07-varaaja.c" osa="rakenne"}
```

Varaus käy lohkot läpi ja valitsee sopivan vapaan. *First fit* ottaa
ensimmäisen riittävän, *best fit* pienimmän riittävän. Jos valittu
lohko on selvästi pyydettyä suurempi, loppu pilkotaan omaksi vapaaksi
lohkokseen:

```{.c tiedosto="esimerkit/07-varaaja.c" osa="varaa"}
```

Vapautus merkitsee lohkon vapaaksi ja yhdistää vierekkäiset vapaat
lohkot (engl. coalescing). Ilman yhdistämistä keko pirstoutuisi
pieniksi paloiksi, vaikka kaikki muisti olisi vapaana:

```{.c tiedosto="esimerkit/07-varaaja.c" osa="vapauta"}
```

Ulkoista pirstoutumista mitataan suurimman vapaan lohkon osuudella
kaikesta vapaasta muistista: $1 - \text{suurin}/\text{vapaata}$.
Kun suurin lohko on puolet vapaasta, pirstoutuminen on 50 %.
Esimerkin funktio `kartta` tulostaa lohkot ja tämän luvun.

## First fit ja best fit

Sama varaussarja ajetaan kummallakin strategialla. Ensin varataan
neljä lohkoa ja vapautetaan niistä kaksi, jolloin keossa on kolme
vapaata aukkoa. Sitten varataan 100, 280 ja 400 tavua, ja lopuksi
kaikki vapautetaan:

```{.tuloste tiedosto="esimerkit/07-varaaja.odotettu"}
```

Merkintä `K128` on 128 tavun varattu lohko otsakkeineen, `V320`
vapaa lohko. First fit pilkkoo 100 tavun pyynnölle keon alun suuren
aukon, vaikka myöhemmin olisi ollut täsmälleen sopiva. 280 tavun pyyntö
ei enää mahdu alkuun, joten se pilkkoo lopun suuren aukon. 400 tavun
pyyntö epäonnistuu, vaikka vapaata on 464 tavua – se on vain kolmena
palana. Best fit käyttää ensin pienimmän sopivan aukon ja säästää
suuret, joten kaikki pyynnöt onnistuvat. Lohkon `K320` hyötykuorma on
24 tavua pyydettyä suurempi: 8 tavua tulee tasauksesta ja 16 tavua
lopusta, jota ei voinut pilkkoa pienimmän lohkokoon alle. Ne ovat
sisäistä pirstoutumista.

Best fit ei ole aina parempi: se jättää pieniä käyttökelvottomia
paloja, ja toisilla varaussarjoilla first fit pirstouttaa vähemmän.

## Nopeammat rakenteet

Implisiittinen lista on opetusväline: varaus on $O(n)$ kaikista
lohkoista, ja vapautus käy esimerkissä koko keon läpi löytääkseen
edellisen lohkon. Todelliset varaajat parantavat kolmella tavalla:

- **Rajamerkit** (engl. boundary tags): kopio otsakkeesta lohkon
  lopussa, joten edeltäjä löytyy ja yhdistäminen on $O(1)$.
- **Eksplisiittinen vapaalista:** vain vapaat lohkot ketjutetaan
  niiden käyttämättömän hyötykuorman kautta.
- **Kokoluokat:** oma vapaalista kullekin kokoluokalle.

glibc:n `malloc` käyttää kokoluokkia, rajamerkkejä, säiekohtaisia
välimuisteja ja useita areenoja. Suuret varaukset (yli 128 KiB) se
tekee suoraan `mmap`-kutsulla.

## Slab-varaaja

Ytimessä varataan jatkuvasti samankokoisia olioita:
prosessikuvaajia, inodeja, avoimia tiedostoja, verkkopaketteja.
*Slab-varaaja* (Bonwick 1994) pitää jokaiselle oliotyypille oman
välimuistin. Välimuisti koostuu slabeista – yhdestä tai useammasta
sivusta, joka on pilkottu valmiiksi olion kokoisiksi paikoiksi. Vapaat
paikat ketjutetaan paikkojen itsensä kautta, joten erillistä
kirjanpitoa ei tarvita:

```{.c tiedosto="esimerkit/07-slab.c" osa="tyypit"}
```

Uusi slab pilkotaan olion kokoisiin paikkoihin, ja jokainen paikka
lisätään vapaalistaan.

Varaus ottaa vapaalistan ensimmäisen paikan, vapautus palauttaa sen
listan alkuun. Molemmat ovat vakioaikaisia, eikä ulkoista
pirstoutumista synny, koska kaikki paikat ovat samankokoisia.
Vapautetun paikan slab siirretään listan alkuun, jotta seuraava varaus
saa juuri vapautetun – todennäköisesti vielä välimuistissa olevan –
paikan:

```{.c tiedosto="esimerkit/07-slab.c" osa="varaa"}
```

Esimerkki varaa sata 64 tavun tiedostokahvaa, vapauttaa yhden,
varaa uuden ja lopuksi vapauttaa kaikki:

```{.tuloste tiedosto="esimerkit/07-slab.odotettu"}
```

Linuxin nykyinen toteutus on SLUB, jossa on suoritinkohtaiset
vapaalistat; tilastot näkyvät komennolla `slabtop`.

## Sivuvaraaja

Slabit ja `malloc`in areenat saavat sivunsa ytimen sivuvaraajalta.
Linuxin *buddy-varaaja* pitää vapaita alueita kahden potenssin
kokoluokissa (1, 2, 4 … 1024 sivua). Pyyntö pyöristetään ylös
seuraavaan potenssiin; jos sopivaa ei ole, suurempi alue jaetaan
kahtia, ja puolikkaat ovat toistensa "kavereita" (engl. buddy).
Vapautuksessa kaveri löytyy osoitteen yhdellä bitillä, ja jos sekin on
vapaa, puolikkaat yhdistetään. Pyöristys ylöspäin aiheuttaa sisäistä
pirstoutumista.

## Käytännössä

- **Älä kirjoita omaa yleiskäyttöistä varaajaa:** C-kirjaston
  `malloc` on vuosikymmenten työ. Erikoisvaraaja kannattaa, kun
  kaikki oliot ovat samankokoisia tai vapautetaan kerralla (areena).
- **Areena lyhytikäisille:** varaa lineaarisesti ja vapauta kaikki
  kerralla esimerkiksi pyynnön käsittelyn lopussa.
- **Mittaa ytimen näkemää muistia, älä varauksia:** `free` palauttaa
  lohkon varaajalle, ei välttämättä ytimelle. Pitkään ajavan
  palvelun muistinkulutus (RSS, `/proc/<pid>/status`) voi kasvaa
  pirstoutumisen takia, vaikka ohjelma ei vuoda.
- **Samankokoiset ja samanikäiset yhteen:** eri-ikäisten ja
  -kokoisten olioiden sekoittaminen samaan kekoon on pirstoutumisen
  tavallisin syy.
- **Sanitoija löytää sen, mitä varaaja ei tarkista:** käyttö
  vapautuksen jälkeen ja ylivuodot näkyvät AddressSanitizerilla heti,
  varaajan omassa kirjanpidossa vasta satunnaisena kaatumisena.

## Itsearviointi

- Osaat toteuttaa implisiittiseen lohkolistaan perustuvan varaajan,
  jossa on pilkkominen ja vapaiden lohkojen yhdistäminen.
- Osaat erottaa sisäisen ja ulkoisen pirstoutumisen ja mitata
  jälkimmäisen.
- Osaat verrata first fit- ja best fit -strategioita ja selittää,
  miksi kumpikaan ei ole aina parempi.
- Osaat kuvata slab-varaajan ja buddy-varaajan periaatteen ja
  kertoa, mihin kumpaakin käytetään.
