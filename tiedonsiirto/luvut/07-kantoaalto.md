# Kantoaallon synkronointi

Lähettimen ja vastaanottimen oskillaattorit ovat erillisiä
kvartsikiteitä, joiden taajuudet eroavat tyypillisesti 1–20 miljoonasosaa
(ppm). 2,4 GHz:n kantoaallolla 10 ppm on 24 kHz:n taajuusvirhe.
Lisäksi vastaanotin ei tiedä kantoaallon vaihetta, koska se riippuu
etäisyydestä. Koherentti ilmaisu edellyttää, että kumpikin virhe
korjataan. Kantataajuudella ne näkyvät konstellaation kiertona:
vaihevirhe kiertää kaikkia pisteitä samalla kulmalla, ja taajuusvirhe
pyörittää konstellaatiota tasaisella nopeudella.

## Virheiden vaikutus

Vaihevirhe siirtää pisteitä kohti päätösrajoja. Tiheässä
konstellaatiossa reunimmaiset pisteet liikkuvat eniten, ja niiden
etäisyys naapureihin on pieni, joten QAM on paljon herkempi
vaihevirheelle kuin QPSK.

![16-QAM kohinassa kahdella signaali-kohinasuhteella ja 10 asteen
vaihevirheellä. Vaihevirhe siirtää uloimpia pisteitä eniten kohti
päätösrajoja.](kuvat/konstellaatio.png){width=100%}

```{.python tiedosto="esimerkit/07-virheet.py" osa="vaihe"}
```

Taajuusvirhe on kantataajuudella kertolasku tekijällä
$e^{i2\pi\Delta f t}$, joten vaihe kasvaa $360\,\Delta f/R_s$ astetta
symbolia kohti:

```{.python tiedosto="esimerkit/07-virheet.py" osa="taajuus"}
```

```{.tuloste tiedosto="esimerkit/07-virheet.odotettu"}
```

Kymmenen asteen vaihevirhe moninkertaistaa kummankin modulaation
virhesuhteen. 20 asteella 16-QAM:n bittivirhesuhde on jo 0,13, kun
QPSK:n on vielä alle prosentin: QPSK:n päätösraja on 45 asteen päässä,
16-QAM:n uloimmilla pisteillä vain noin 17 asteen päässä. 200 Hz:n
taajuusvirhe megasymbolin nopeudella vaikuttaa pieneltä (0,02 %
symbolinopeudesta), mutta tuhannen symbolin paketissa konstellaatio
on kiertynyt 72 astetta. Siksi vaihetta on seurattava koko paketin ajan
eikä vain alussa.

## Taajuusvirheen avoin estimointi

Suuri taajuusvirhe korjataan ennen silmukkaa avoimella estimaatilla,
koska kapea silmukka ei lukitu, jos virhe on sen kaistaa suurempi.
QPSK:n jokaisen symbolin neljäs potenssi on sama luku $-1$, joten
signaalin $r[n] = s[n]\,e^{i(2\pi f n + \varphi)}$ neljäs potenssi on
modulaatiosta riippumaton sini taajuudella $4f$. Sen taajuus löytyy
FFT:n huipusta. BPSK:lle vastaava temppu on toinen potenssi ja
$M$-PSK:lle $M$:s potenssi.

```{.python tiedosto="esimerkit/07-taajuus.py" osa="potenssi"}
```

```{.python tiedosto="esimerkit/07-taajuus.py" osa="koe"}
```

```{.tuloste tiedosto="esimerkit/07-taajuus.odotettu"}
```

Estimaatti on tarkka 10 dB:n signaali-kohinasuhteella, mutta sen alue
on rajattu: $4f$ on yksikäsitteinen vain välillä $\pm 1/2$, joten
taajuusvirheen on oltava alle $1/8$ symbolinopeudesta. Taajuus 0,13
näkyy taajuutena $0{,}13 - 0{,}25 = -0{,}12$. Potenssiin korottaminen
myös vahvistaa kohinaa, joten pienellä signaali-kohinasuhteella
estimaatti heikkenee nopeasti. Tunnettu alkuosa (luku 11) on usein
parempi lähtökohta, jos paketissa sellainen on.

## Vaihelukittu silmukka

Vaihetta seurataan **vaihelukitulla silmukalla** (PLL, *phase-locked
loop*). Silmukassa on kolme osaa:

1. **Vaihevirheilmaisin** laskee jokaisesta korjatusta symbolista
   arvion jäljellä olevasta vaihevirheestä.
2. **Silmukkasuodin** (PI-säädin) suodattaa virhearvion. Sen
   integroiva osa oppii taajuusvirheen.
3. **NCO** (*numerically controlled oscillator*) kertyttää vaiheen ja
   kiertää seuraavaa symbolia sen verran takaisin.

Toisen asteen silmukan vahvistukset lasketaan halutusta
kohinakaistasta $B_nT$ ja vaimennuksesta $\zeta$. Kapea kaista
suodattaa kohinaa tehokkaasti, mutta lukittuu hitaasti. Tavallinen
lähtökohta on $\zeta = 1/\sqrt2$ ja $B_nT$ = 0,005–0,05.

```{.python tiedosto="esimerkit/07-costas.py" osa="vahvistukset"}
```

QPSK:n moduloitu signaali ei sisällä kantoaaltoa, joten virhettä ei voi
mitata suoraan. **Costas-silmukka** vertaa vastaanotettua symbolia sen
lähimpään konstellaatiopisteeseen. QPSK:lle virhe on
$\operatorname{sign}(I)\,Q - \operatorname{sign}(Q)\,I$, joka on nolla,
kun symboli on akseleiden välissä, ja verrannollinen vaihevirheeseen
pienillä virheillä.

```{.python tiedosto="esimerkit/07-costas.py" osa="silmukka"}
```

Kokeessa on 0,002 sykliä symbolia kohti taajuusvirhe ja yhden radiaanin
vaihevirhe. Ensimmäisen asteen silmukassa (vain P-osa) ei ole
integraattoria:

```{.python tiedosto="esimerkit/07-costas.py" osa="koe"}
```

## Neljän kulman epävarmuus

QPSK näyttää samalta, jos sitä kierretään 90 astetta, joten silmukka
lukittuu yhteen neljästä mahdollisesta vaiheesta. Bitit ovat oikein vain
yhdessä niistä. Epävarmuus ratkaistaan joko tunnetulla
**tahdistussanalla**, jonka avulla vastaanotin valitsee oikean kierron,
tai **differentiaalisella koodauksella**, jossa tieto on peräkkäisten
symbolien vaihe-erossa. Differentiaalinen koodaus ei tarvitse
tahdistussanaa, mutta yksi symbolivirhe aiheuttaa kaksi virhettä.

```{.python tiedosto="esimerkit/07-costas.py" osa="epavarmuus"}
```

```{.tuloste tiedosto="esimerkit/07-costas.odotettu"}
```

Ensimmäisen asteen silmukka seuraa taajuusvirhettä, mutta 13 asteen
pysyvällä vaihevirheellä: vaihevirheilmaisimen lähdön on oltava nollasta
poikkeava, jotta NCO pyörisi oikealla nopeudella. Toisen asteen silmukan
integraattori oppii taajuuden, ja jäännösvirhe putoaa lähes nollaan.
Lopputuloksessa silmukka oli lukittunut 270 asteen päähän oikeasta
vaiheesta, ja tahdistussana korjasi sen.

## Käytännössä

- **Karkea ja tarkka vaihe.** Suuri taajuusvirhe korjataan ensin
  avoimella estimaattorilla (esim. alkuosan vaihe-erolla, luku 11) ja
  vasta sitten silmukalla, koska kapeakaistainen silmukka ei lukitu, jos
  virhe on kaistaa suurempi.
- **Valitse silmukan kaista kohinan ja dynamiikan väliltä.** Laske
  vahvistukset kaavoista ja tarkista lukittumisaika ja jäännösvirhe
  simuloimalla. Kaksinkertainen kaista puolittaa lukittumisajan ja
  kasvattaa vaihekohinaa.
- **Ratkaise epävarmuus.** Käytä tahdistussanaa, pilotteja tai
  differentiaalista koodausta. Ilman niitä vastaanotin voi toimia
  täydellisesti väärillä biteillä.
- **Tiheät konstellaatiot tarvitsevat hyvän oskillaattorin.**
  Oskillaattorin vaihekohina on 64- ja 256-QAM:n yleinen rajoite, eikä
  silmukka voi seurata kaistaansa nopeampaa vaihekohinaa.

## Itsearviointi

- Osaat selittää, miten vaihe- ja taajuusvirhe näkyvät konstellaatiossa,
  ja arvioida niiden vaikutuksen eri modulaatioihin.
- Osaat estimoida QPSK:n taajuusvirheen neljännellä potenssilla ja
  kertoa estimaattorin alueen.
- Osaat toteuttaa toisen asteen vaihelukitun silmukan ja laskea sen
  vahvistukset kaistasta ja vaimennuksesta.
- Osaat selittää Costas-silmukan vaihevirheilmaisimen ja sen, miksi
  ensimmäisen asteen silmukkaan jää pysyvä virhe taajuusvirheen kanssa.
- Osaat ratkaista neljän kulman epävarmuuden tahdistussanalla tai
  differentiaalisella koodauksella.
