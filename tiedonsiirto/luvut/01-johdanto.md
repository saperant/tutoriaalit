# Johdanto {.runko-johdanto}

Radio, kuitu ja kupari siirtävät jatkuvia aaltomuotoja, mutta niiden
avulla halutaan siirtää bittejä. Digitaalinen tiedonsiirto on
menetelmien kokoelma, jolla bitit muutetaan aaltomuodoiksi ja takaisin
niin, että kohina, häipyminen ja laitteiden epätarkkuudet tuottavat
mahdollisimman vähän virheitä mahdollisimman kapealla kaistalla ja
pienellä teholla. Samat menetelmät ovat matkapuhelimessa, WLAN-
tukiasemassa, kaapelimodeemissa, satelliittivastaanottimessa ja
kuitulinkin vastaanottimessa.

Tutoriaali käy läpi lähettimen ja vastaanottimen koko ketjun ja
simuloi jokaisen vaiheen Pythonilla. Simulaatio on tiedonsiirron
insinöörin tärkein työkalu: jokainen algoritmi tarkistetaan ensin
simulaatiolla teoreettista tulosta vastaan, ennen kuin se toteutetaan
laitteistolla tai ohjelmistoradiolla. Jokainen esimerkki käyttää
kiinteää satunnaissiementä, joten tulokset ovat toistettavia ja
testattavia.

## Ensimmäinen esimerkki: koko ketju

Seuraava ohjelma lähettää 200 000 bittiä QPSK-modulaatiolla kohinaisen
kanavan yli. Ensin tehdään **pulssi**, jonka muoto rajaa signaalin
kaistan. Pulssin yksityiskohdat käsitellään luvussa 5.

```{.python tiedosto="esimerkit/01-ketju.py" osa="pulssi"}
```

Lähetin ryhmittelee bitit pareiksi ja tekee kustakin parista
kompleksiluvun, **symbolin**. Symbolit sijoitetaan kahdeksan näytteen
välein ja suodatetaan pulssilla. Tuloksena on kantataajuinen
kompleksinen signaali, jonka radio sekoittaisi kantoaallolle.

```{.python tiedosto="esimerkit/01-ketju.py" osa="lahetin"}
```

Kanava lisää valkoista Gaussin kohinaa. Kohinan taso lasketaan
suureesta $E_b/N_0$, bitin energian ja kohinan tehotiheyden suhteesta,
joka on tiedonsiirron tärkein mittayksikkö (luku 6).

```{.python tiedosto="esimerkit/01-ketju.py" osa="kanava"}
```

Vastaanotin suodattaa signaalin samalla pulssilla, ottaa näytteen
kunkin symbolin kohdalta ja päättelee bitit näytteen etumerkeistä.
Lopuksi virheiden määrää verrataan teoreettiseen bittivirhesuhteeseen.

```{.python tiedosto="esimerkit/01-ketju.py" osa="vastaanotin"}
```

```{.tuloste tiedosto="esimerkit/01-ketju.odotettu"}
```

Simuloitu bittivirhesuhde osuu teoriaan, kun otetaan huomioon, että 453
virhettä on satunnaismuuttuja, jonka suhteellinen keskihajonta on noin
$1/\sqrt{453} \approx 5$ %. Tämä vertailu on jokaisen
tiedonsiirtosimulaation perusta: kun ketju on oikein, tulos noudattaa
teoriaa, ja kun jokin osa on väärin (väärä kohinan taso, väärä
näytehetki, puuttuva sovitettu suodin), tulos poikkeaa siitä
selvästi.

Esimerkissä on koko tutoriaalin runko. Seuraavat luvut avaavat sen osat
ja lisäävät todellisen kanavan ongelmat: vastaanottimen kello ja
kantoaalto eivät ole samassa tahdissa lähettimen kanssa, kanava
vääristää pulssia, ja bittivirheitä on korjattava. Seuraava kaavio on
tutoriaalin kartta: yhtenäiset laatikot ovat esimerkin vaiheet, ja
katkoviivalla merkityt lisätään myöhemmissä luvuissa.

```{.dot otsikko="Siirtoketju ja luvut, joissa sen osat käsitellään"}
digraph ketju {
  rankdir=TB; nodesep=0.3; ranksep=0.35;
  node [shape=box, fontsize=10];
  bitit [label="bitit", shape=plaintext];
  koodaus [label="koodaus\n(luku 9)", style=dashed];
  symbolit [label="symbolit\n(luku 4)"];
  pulssi [label="pulssi\n(luku 5)"];
  kanava [label="kanava: kohina,\nvaihe, viive (luku 6)", shape=ellipse];
  sovitettu [label="sovitettu suodin\n(luku 5)"];
  tahdistus [label="tahdistus\n(luvut 7–8)", style=dashed];
  paatos [label="päätös\n(luku 4)"];
  dekoodaus [label="dekoodaus\n(luku 9)", style=dashed];
  ulos [label="bitit", shape=plaintext];
  { rank=same; bitit -> koodaus -> symbolit -> pulssi; }
  pulssi -> kanava -> sovitettu;
  { rank=same;
    ulos -> dekoodaus -> paatos -> tahdistus -> sovitettu [dir=back]; }
}
```

## Esitiedot ja rajaus

Lukija osaa Pythonin ja NumPyn sekä signaalinkäsittelyn perusteet:
kompleksiluvut ja Eulerin kaavan (taito *Kompleksiluvut ja
Fourier-analyysi*), konvoluution, taajuusvasteen ja DFT:n (*Signaalit
ja järjestelmät*) sekä FIR-suotimet, desimoinnin ja interpoloinnin
(*Digitaalinen signaalinkäsittely*). Normaalijakauma, odotusarvo ja
varianssi tulevat taidosta *Todennäköisyys ja tilastot*. Taito
*Tietoliikennetekniikka* kertoo siirtoteistä, Shannonin rajasta,
linkkibudjetista ja pariteetista, CRC:stä ja Hamming-koodista
yleistasolla. Tässä tutoriaalissa samoihin aiheisiin palataan
simuloiden ja syvemmin, mutta perusteita ei toisteta.

Rajauksia on kolme. Yhden kantoaallon taajuuskorjain (kanavan
vääristymän poisto adaptiivisella suotimella) jää pois; sen työkalu,
LMS-suodin, on taidossa *Digitaalinen signaalinkäsittely*, ja OFDM-luku
näyttää toisen tavan ratkaista sama ongelma. Nykyaikaiset koodit
(LDPC, turbo, polaarikoodit) esitellään vain periaatteena. Oikean
radion epäideaalisuudet ja laitteet ovat taidossa *Ohjelmistoradio*.
Esimerkit ajetaan komennolla `make testaa` tai yksitellen, esimerkiksi
`python3 esimerkit/01-ketju.py`.

| Luku | Kysymys |
|---------------------|--------------------------------------------|
| Kantataajuus ja kaistanpäästö | Miksi radiosignaalia käsitellään kompleksilukuina? |
| Analogiset modulaatiot | Miten AM ja FM toimivat, ja mitä niistä opitaan? |
| Digitaaliset modulaatiot | Montako bittiä symboliin mahtuu, ja miten ne nimetään? |
| Pulssinmuokkaus | Miten symbolit eivät häiritse toisiaan kapealla kaistalla? |
| Kohina ja BER | Paljonko virheitä tietyllä teholla tulee, ja missä on raja? |
| Kantoaallon synkronointi | Miten vastaanotin korjaa vaihe- ja taajuusvirheen? |
| Symboli- ja kehystahdistus | Milloin näyte otetaan, ja mistä kehys alkaa? |
| Kanavakoodaus | Miten virheet korjataan, ja paljonko se säästää tehoa? |
| OFDM | Miten monitiekanavasta tehdään helppo? |
| Kokonainen linkki | Miten osat liitetään yhteen ja simulaatio testataan? |

## Merkinnät ja yksiköt

Tutoriaali käyttää kantataajuista mallia: signaali on jono
kompleksilukuja, ja kantoaalto on mukana vain luvuissa 2 ja 3. Symbolin
energia normitetaan ykköseksi ($E_s = 1$), joten kohinan taso
määräytyy yhdestä luvusta $N_0$. Tärkeimmät merkinnät:

| Merkintä | Merkitys |
|------------------|----------------------------------------|
| $T$, $R_s = 1/T$ | symbolin kesto ja symbolinopeus |
| $M$, $k = \log_2 M$ | konstellaation pisteiden määrä ja bittejä symbolia kohti |
| $E_s$, $E_b = E_s/k$ | symbolin ja bitin energia |
| $N_0$ | kohinan tehotiheys (yksipuolinen) |
| `sps` | näytteitä symbolia kohti |
| BER, SER, PER | bitti-, symboli- ja pakettivirhesuhde |
| $Q(x)$ | normaalijakauman häntä $P(X > x)$, $X \sim N(0, 1)$ |

Kaikki esimerkit toimivat Python 3.12:lla ja uudemmilla, ja ne
tarvitsevat NumPyn ja SciPyn. Ne tarkistetaan ruffilla ja
`mypy --strict` -tarkistuksella, ja kahden luvun kirjastot testataan
pytestillä. Kehityskontissa työkalut ovat valmiina.
