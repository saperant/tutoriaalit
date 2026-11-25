# Differenssimenetelmä: tasapainotila

Differenssimenetelmä on suorin tapa muuttaa differentiaaliyhtälö
yhtälöryhmäksi: kenttä tunnetaan hilapisteissä, ja derivaatat korvataan
naapuriarvojen erotuksilla. Johdannossa menetelmää käytettiin jo
yksinkertaisimmassa tapauksessa. Tässä luvussa käsitellään kolme asiaa,
jotka ratkaisevat, toimiiko se oikeissa tehtävissä: aineiden rajapinnat,
reunaehtojen tarkkuus ja siirtyminen kahteen ulottuvuuteen. Aika tulee
mukaan luvussa 4.

## Erotusosamäärä ja sen virhe

Taylorin kehitelmistä pisteen $x_i$ ympärillä seuraa

$$\frac{u_{i-1} - 2u_i + u_{i+1}}{h^2}
  = u''(x_i) + \frac{h^2}{12}\,u''''(x_i) + \dots$$

Toinen differenssi on siis toista kertalukua: virhe on verrannollinen
$h^2$:een ja ratkaisun neljänteen derivaattaan. Tästä seuraa kaksi
asiaa. Toisen asteen polynomille kaava on tarkka, ja jos ratkaisussa on
taite tai hyppy (neljäs derivaatta ei ole rajoitettu), luvattu kertaluku
ei päde. Jälkimmäinen on käytännön tehtävissä sääntö eikä poikkeus:
aineiden rajat, nurkat ja kuormien reunat tuottavat taitteita.

Yhtälö $-(k u')' = s$ diskretoidaan luvun 2 säännön mukaan taseena.
Kontrollitilavuuden $i$ yhtälö on

$$-k_{i+1/2}\,\frac{u_{i+1} - u_i}{h}
  + k_{i-1/2}\,\frac{u_i - u_{i-1}}{h} = h\,s_i,$$

jossa $k_{i\pm1/2}$ on rajapinnan johtavuus. Vakiojohtavuudella tämä on
sama kuin toinen differenssi.

## Aineiden rajapinta

Ulkoseinässä on 130 mm tiiltä ja 100 mm mineraalivillaa. Sisällä on
21 °C ja ulkona −15 °C. Stationaarinen lämpövirta tunnetaan tarkasti,
koska kerrokset ovat lämpövastuksina sarjassa:
$q = \Delta T / (L_1/k_1 + L_2/k_2)$.

Hilassa aineiden raja osuu kahden kontrollitilavuuden väliin, ja
rajapinnalle tarvitaan yksi johtavuuden arvo. Vaihtoehtoja on kaksi:
viereisten tilavuuksien aritmeettinen keskiarvo tai harmoninen
keskiarvo $2k_1k_2/(k_1 + k_2)$.

```{.python tiedosto="esimerkit/03-seina.py" osa="kokoaminen"}
```

```{.python tiedosto="esimerkit/03-seina.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/03-seina.odotettu"}
```

Harmoninen keskiarvo antaa tarkan tuloksen jo 23 tilavuudella, koska se
on juuri kahden puolikkaan sarjaankytkentä: se on vastusmalli pienessä
koossa. Aritmeettinen keskiarvo yliarvioi rajapinnan johtavuuden
(0,32 eikä 0,068 W/(m K)) ja päästää lämpöä läpi neljä prosenttia
liikaa. Virhe pienenee hilaa tihentämällä, mutta vain ensimmäisessä
kertaluvussa.

Esimerkissä on toinenkin yksityiskohta: reunimmaisen tilavuuden
keskipiste on puolen hilavälin päässä pinnasta, joten pinnan ja
keskipisteen välinen johtavuus on $2k/h$ eikä $k/h$. Solukeskinen hila
(arvot tilavuuksien keskellä) tekee rajapinnoista helppoja ja
Dirichlet'n reunasta hieman mutkikkaamman. Solmukeskinen hila (arvot
pisteissä, joista osa on reunalla) toimii päinvastoin. Loppuluvussa
käytetään solmukeskistä hilaa.

## Vuoreunaehto ja haamupiste

Jäähdytysrivan tyvi on 100 °C ja kärki eristetty: $u'(L) = 0$. Kärjen
pisteellä ei ole oikeanpuoleista naapuria, joten sen yhtälö on
rakennettava reunaehdosta. Tapoja on kaksi.

**Toispuoleinen erotus** korvaa ehdon yhtälöllä
$(u_n - u_{n-1})/h = 0$. Se on helppo, mutta vain ensimmäistä
kertalukua.

**Haamupiste** kuvittelee hilan jatkuvan yhden pisteen reunan yli.
Keskeisdifferenssi $(u_{n+1} - u_{n-1})/(2h) = 0$ antaa haamupisteen
arvon $u_{n+1} = u_{n-1}$, ja se sijoitetaan kärjen tavalliseen
yhtälöön. Tulos on toista kertalukua. Sama yhtälö syntyy, kun kärjen
puolikkaalle kontrollitilavuudelle kirjoitetaan tase, joten haamupiste
on säilyvä muoto reunalla.

```{.python tiedosto="esimerkit/03-neumann.py" osa="ripa"}
```

```{.python tiedosto="esimerkit/03-neumann.py" osa="kertaluku"}
```

```{.tuloste tiedosto="esimerkit/03-neumann.odotettu"}
```

Yhden reunapisteen ensimmäisen kertaluvun yhtälö pudottaa **koko
ratkaisun** ensimmäiseen kertalukuun, vaikka kaikki muut yhtälöt ovat
toista kertalukua. 160 välillä ero on viisisataakertainen. Ratkaisun
kertaluku on heikoimman osansa kertaluku, ja heikoin osa on tavallisesti
reunaehto.

## Kaksi ulottuvuutta: lämpötila levyssä

Neliölevyn alareuna pidetään 100 asteessa ja muut reunat nollassa.
Tasapainossa lämpötila toteuttaa Laplacen yhtälön
$u_{xx} + u_{yy} = 0$. Kun kumpikin derivaatta korvataan toisella
differenssillä samalla hilavälillä, saadaan **viiden pisteen kaava**:

$$4u_{i,j} - u_{i-1,j} - u_{i+1,j} - u_{i,j-1} - u_{i,j+1} = h^2 s_{i,j}.$$

Lähteettömässä tapauksessa jokainen arvo on neljän naapurinsa
keskiarvo. Kaava on myös tase: neliön muotoiseen kontrollitilavuuteen
neljältä sivulta tuleva lämpö summautuu nollaan.

Tuntemattomat numeroidaan riveittäin, jolloin matriisi on harva ja
siinä on viisi lävistäjää. Se kootaan Kroneckerin tulolla
yksiulotteisesta matriisista; harva tallennus ja suora ratkaisija ovat
tuttuja taidosta *Numeeriset menetelmät*. Reunapisteiden tunnetut arvot
siirtyvät yhtälön oikealle puolelle.

```{.python tiedosto="esimerkit/03-levy.py" osa="kokoaminen"}
```

Tälle tehtävälle on sarjaratkaisu, johon numeerista tulosta voi
verrata:

```{.python tiedosto="esimerkit/03-levy.py" osa="sarja"}
```

```{.python tiedosto="esimerkit/03-levy.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/03-levy.odotettu"}
```

![Levyn lämpötila ja tasa-arvokäyrät 10, 25, 50 ja 75 °C. Lämpövirta
kulkee kohtisuoraan tasa-arvokäyriä vastaan. Alanurkissa kuuma ja kylmä
reuna kohtaavat, ja kaikki tasa-arvokäyrät päätyvät
niihin.](kuvat/levy.png){width=62%}

Taulukossa on kaksi havaintoa. Ensimmäinen on **symmetriatarkistus**:
keskipisteen lämpötila on täsmälleen 25 °C kaikilla hiloilla. Jos
kuuma reuna kierretään vuorotellen jokaiselle sivulle ja neljä ratkaisua
lasketaan yhteen, tuloksena on levy, jonka kaikki reunat ovat 100 °C,
ja sen lämpötila on kaikkialla 100. Keskipiste saa jokaisesta
ratkaisusta saman osuuden, siis neljäsosan. Päättely pätee myös
diskreetille yhtälölle, joten poikkeama arvosta 25 paljastaisi virheen
kokoamisessa. Tällaiset tarkistukset ovat arvokkaita, koska ne eivät
vaadi tarkkaa ratkaisua.

Toinen havainto on kertaluku: pisteessä (0,5; 0,25) virhe pienenee
kuten $h^2$, vaikka alanurkissa reuna-arvo on epäjatkuva ja ratkaisun
derivaatat kasvavat siellä rajatta. Elliptisessä tehtävässä häiriö
vaimenee nopeasti etäisyyden kasvaessa, joten nurkan epätarkkuus ei
leviä kauas. Aivan nurkan vieressä virhe ei pienene samaa tahtia. Luku 7
näyttää tapauksen, jossa nurkka pilaa kertaluvun koko alueessa.

## Käytännössä

- **Rajapinnan johtavuus on harmoninen keskiarvo.** Aseta hila niin,
  että aineiden raja osuu tilavuuksien väliin. Jos raja kulkee
  tilavuuden läpi, tulos on ensimmäistä kertalukua riippumatta
  keskiarvosta.
- **Reunaehdot samalla kertaluvulla kuin sisäpisteet.** Haamupiste tai
  puolikkaan tilavuuden tase, ei toispuoleista erotusta.
- **Mittaa kertaluku aina.** Kolme hilaa, joista jokainen on kaksi
  kertaa edellistä tiheämpi, ja virheiden suhde. Jos suhde ei ole
  neljä, etsi syy ennen kuin jatkat.
- **Differenssimenetelmän vahvuus on yksinkertaisuus.** Suorakulmaisessa
  alueessa ja tasavälisellä hilalla se on nopein ja helpoin. Kaareva
  reuna, paikallinen tihennys ja mutkikkaat reunaehdot ovat sille
  hankalia, ja niissä elementtimenetelmä (luvut 6–9) on parempi.
- **Hilan numerointi on virhelähde.** Päätä kerralla, kumpi indeksi on
  $x$ ja kumpi $y$, ja testaa epäsymmetrisellä tehtävällä: neliö ja
  symmetrinen kuorma piilottavat vaihtuneet indeksit.

## Itsearviointi

- Osaat johtaa toisen differenssin katkaisuvirheen Taylorin
  kehitelmästä ja kertoa, milloin luvattu kertaluku ei päde.
- Osaat diskretoida yhtälön $-(k u')' = s$ säilyvässä muodossa ja
  perustella harmonisen keskiarvon rajapinnalla.
- Osaat toteuttaa vuoreunaehdon haamupisteellä ja selittää, miksi
  ensimmäisen kertaluvun reunaehto heikentää koko ratkaisun.
- Osaat koota viiden pisteen kaavan harvaksi matriisiksi ja ratkaista
  levyn tasapainolämpötilan.
- Osaat keksiä tehtävälle symmetriaan tai superpositioon perustuvan
  tarkistuksen, joka ei vaadi tarkkaa ratkaisua.
