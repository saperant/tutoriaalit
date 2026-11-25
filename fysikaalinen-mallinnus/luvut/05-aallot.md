# Aallot ja CFL-ehto

Lämpöyhtälö tasoittaa, aaltoyhtälö kuljettaa. Aalto etenee
äärellisellä nopeudella ja säilyttää muotonsa ja energiansa, ja hyvän
numeerisen menetelmän pitää tehdä samoin. Tässä luvussa ratkaistaan
värähtelevä kieli ja kalvo, johdetaan aika-askeleen yläraja, jota
kutsutaan CFL-ehdoksi, ja mitataan simulaatiosta suure, jota insinööri
yleensä haluaa: ominaistaajuudet.

## Keskeisdifferenssit ajassa ja paikassa

Aaltoyhtälössä $u_{tt} = c^2 u_{xx}$ on toinen derivaatta sekä ajan
että paikan suhteen. Kun molemmat korvataan toisella differenssillä,
saadaan kaavio

$$u_i^{n+1} = 2u_i^n - u_i^{n-1}
  + C^2\,(u_{i-1}^n - 2u_i^n + u_{i+1}^n),
  \qquad C = \frac{c\,\Delta t}{h}.$$

Luku $C$ on **Courantin luku**: matka, jonka aalto kulkee yhden
aika-askeleen aikana, hilaväleinä mitattuna. Kaavio tarvitsee kaksi
edellistä aikatasoa. Ensimmäinen askel otetaan alkuehdoista Taylorin
kehitelmällä, jossa $u_{tt}$ korvataan yhtälön avulla paikan
derivaatalla; näin aloituskin on toista kertalukua.

```{.python tiedosto="esimerkit/05-kieli.py" osa="askel"}
```

Kaavio on eksplisiittinen: uusi arvo saadaan suoraan vanhoista, eikä
yhtälöryhmää ratkaista. Aalloille se on oikea valinta, toisin kuin
lämpöyhtälölle. Syy selviää seuraavasta osiosta.

## Näppäilty kieli

Kieli vedetään kolmioksi kohdasta 0,3 ja päästetään irti. Tarkassa
ratkaisussa taite jakautuu kahdeksi, jotka kulkevat vastakkaisiin
suuntiin, heijastuvat päistä ylösalaisin ja palaavat. Jakson $2L/c$
jälkeen kieli on täsmälleen alkuasennossaan. Tästä saadaan tarkistus,
joka ei vaadi ratkaisun kaavaa.

Toinen tarkistus on energia. Kaaviolla on oma diskreetti energiansa,
jonka se säilyttää tarkasti:

```{.python tiedosto="esimerkit/05-kieli.py" osa="energia"}
```

```{.python tiedosto="esimerkit/05-kieli.py" osa="koe"}
```

```{.tuloste tiedosto="esimerkit/05-kieli.odotettu"}
```

![Vasemmalla kielen muoto puolen jakson aikana viidellä hetkellä, kun
Courantin luku on 1: taitteet pysyvät terävinä. Oikealla kieli yhden
jakson jälkeen, kun Courantin luku on 0,5: taitteen ympärille on
syntynyt väreilyä.](kuvat/kieli.png){width=95%}

Courantin luvulla 1 tulos on tarkka pyöristysvirhettä vaille, vaikka
alkutilassa on taite. Tämä ei ole sattumaa: silloin aalto kulkee
askeleessa täsmälleen yhden hilavälin, ja kaavio siirtää arvoja
pisteestä toiseen ilman interpolointia.

Pienemmällä Courantin luvulla virhe on muutamia prosentteja, ja se on
tietynlaista: **numeerista dispersiota**. Kaaviossa lyhyet aallot
etenevät hitaammin kuin pitkät, joten terävä taite, joka koostuu
monista aallonpituuksista, hajoaa väreilyksi. Energia säilyy silti
kaikissa kolmessa ajossa. Menetelmä ei siis vaimenna aaltoa, se vain
kuljettaa sen osia hieman väärällä nopeudella. Dispersio pienenee
hilaa tihentämällä: sääntönä on vähintään kymmenen hilaväliä lyhintä
kiinnostavaa aallonpituutta kohden.

Tässä näkyy myös ero lämpöyhtälöön. Aaltoyhtälön ratkaisu ei tasoitu,
joten pitkä implisiittinen askel hukkaisi juuri sen tiedon, jota
haetaan. Tarkkuus vaatii joka tapauksessa askeleen, joka on lähellä
arvoa $h/c$, ja sillä askeleella eksplisiittinen kaavio on stabiili ja
halvin.

## CFL-ehto

Kaavion uusi arvo pisteessä $i$ riippuu vain pisteistä $i-1$, $i$ ja
$i+1$. Tieto voi siis edetä hilassa enintään yhden välin askeleessa,
nopeudella $h/\Delta t$. Jos todellinen aalto on tätä nopeampi, kaavio
ei voi mitenkään tietää, mitä pisteeseen on saapumassa. Tästä seuraa
**Courantin, Friedrichsin ja Lewyn ehto** eli CFL-ehto:

$$C = \frac{c\,\Delta t}{h} \le 1.$$

Ehto on välttämätön mille tahansa eksplisiittiselle kaaviolle: kaavion
riippuvuusalueen pitää sisältää yhtälön riippuvuusalue. Tälle kaaviolle
se on myös riittävä. Kun ehto rikotaan, korkein hilataajuus kasvaa joka
askeleella kertoimella $2C^2 - 1 + \sqrt{(2C^2 - 1)^2 - 1}$.

```{.python tiedosto="esimerkit/05-cfl.py" osa="koe"}
```

```{.tuloste tiedosto="esimerkit/05-cfl.odotettu"}
```

Yhden prosentin ylitys kasvattaa ratkaisun kolmessasadassa askeleessa
kertaluokkaan $10^{30}$, ja mitattu kasvunopeus vastaa ennustetta.
Kuten lämpöyhtälössä, raja on jyrkkä eikä sen lähellä ole
varoitusmerkkejä.

Rajan hinta on kuitenkin toinen. Lämpöyhtälössä $\Delta t$ oli
verrannollinen $h^2$:een, tässä $h$:hon. Kun hila tihennetään
kaksinkertaiseksi, askelia tarvitaan kaksinkertainen määrä, mikä on
sama tarkkuusvaatimus, jonka aalto asettaisi muutenkin.

Kahdessa ulottuvuudessa samalla hilavälillä kumpaankin suuntaan ehto on
$C \le 1/\sqrt2$ ja kolmessa $C \le 1/\sqrt3$. Jos aallon nopeus
vaihtelee, ehdon määrää nopein kohta ja pienin hilaväli. Yksi pieni
elementti tiheässä kohdassa määrää siis koko mallin aika-askeleen.

## Kalvon ominaistaajuudet

Neliön muotoinen kalvo on kiinni reunoiltaan. Sen liikettä kuvaa
kaksiulotteinen aaltoyhtälö $u_{tt} = c^2 (u_{xx} + u_{yy})$, ja kaavio
on sama kuin kielellä, kun toisen differenssin paikalle tulee viiden
pisteen kaava. Kalvon keskelle tehdään kuoppa, se päästetään irti, ja
keskipisteen liike tallennetaan.

```{.python tiedosto="esimerkit/05-kalvo.py" osa="simulointi"}
```

Liike näyttää sekavalta, mutta se on summa kalvon ominaismuodoista,
joista jokainen värähtelee omalla taajuudellaan. Taajuudet löytyvät
aikasarjan spektristä. Spektrin laskenta, ikkunointi ja nollilla
täyttäminen ovat taidon *Signaalit ja järjestelmät* asiaa; tässä
riittää tieto, että aikasarjan pituus $T$ rajaa taajuuden erottelun
arvoon $1/T$.

```{.python tiedosto="esimerkit/05-kalvo.py" osa="spektri"}
```

```{.tuloste tiedosto="esimerkit/05-kalvo.odotettu"}
```

![Vasemmalla kalvon keskipisteen liike simulaation alussa. Oikealla
koko aikasarjan spektri ja tarkat ominaistaajuudet katkoviivoina.
Jokainen huippu on yksi ominaismuoto.](kuvat/kalvo.png){width=95%}

Viisi alinta herätettyä taajuutta osuvat tarkkoihin arvoihin
neljännesprosentin sisällä. Huippuja puuttuu: symmetrinen kuoppa
keskellä ei herätä muotoja, joilla on solmuviiva keskipisteen kautta,
eikä keskipisteestä mitattu liike näkisi niitä muutenkaan. Sama pätee
oikeissa mittauksissa: iskun ja anturin paikka määräävät, mitkä muodot
näkyvät.

Ominaistaajuudet voi laskea myös suoraan ominaisarvotehtävänä ilman
aikasimulaatiota. Se on yleensä parempi tapa, ja siihen palataan
luvussa 10. Aikasimulaatiota tarvitaan silti, kun halutaan tietää,
kuinka voimakkaasti kukin muoto herää tietyllä kuormalla.

## Käytännössä

- **Aallot eksplisiittisesti, diffuusio implisiittisesti.**
  Aaltotehtävässä tarkkuus vaatii lyhyen askeleen joka tapauksessa.
  Poikkeus on tilanne, jossa pieni osa hilasta on hyvin tiheä tai
  aine hyvin jäykkä: silloin implisiittinen menetelmä tai paikallinen
  aika-askel voi kannattaa.
- **Valitse Courantin luku läheltä rajaa.** Dispersio on pienin lähellä
  stabiilisuusrajaa. Jätä pieni marginaali (esimerkiksi 0,9 kertaa
  raja), koska oikeissa malleissa nopeus ja hilaväli vaihtelevat.
- **Seuraa energiaa.** Häviöttömässä mallissa kokonaisenergia on vakio.
  Kasvava energia kertoo epästabiiliudesta jo ennen kuin tulos näyttää
  väärältä, ja vähenevä energia paljastaa numeerisen vaimennuksen.
- **Kymmenen hilaväliä aallonpituutta kohden.** Arvioi lyhin
  kiinnostava aallonpituus $c/f_{\max}$ ja mitoita hila siitä.
- **Terävät alkutilat värähtelevät.** Taite tai porras sisältää
  kaikkia aallonpituuksia, ja lyhyimmät niistä kulkevat hilassa väärin.
  Jos mahdollista, pyöristä kuorman alku ja loppu fysikaalisesti
  järkevään nousuaikaan.
- **Simulaation pituus määrää taajuuserottelun.** Kaksi ominaistaajuutta
  erottuu toisistaan vasta, kun aikasarja on pidempi kuin niiden eron
  käänteisluku.

## Itsearviointi

- Osaat kirjoittaa aaltoyhtälön keskeisdifferenssikaavion ja selittää,
  miten ensimmäinen aika-askel otetaan.
- Osaat perustella CFL-ehdon riippuvuusalueilla ja kertoa, miten se
  muuttuu kahdessa ulottuvuudessa ja epätasaisessa hilassa.
- Osaat selittää, mitä numeerinen dispersio on, miten se eroaa
  vaimennuksesta ja miten sitä pienennetään.
- Osaat käyttää jaksollisuutta ja energian säilymistä aaltosimulaation
  tarkistuksena.
- Osaat mitata rakenteen ominaistaajuudet aikasimulaation spektristä ja
  tiedät, miksi kaikki muodot eivät näy.
