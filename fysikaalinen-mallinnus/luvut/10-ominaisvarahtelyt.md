# Ominaisvärähtelyt ja aikariippuvat tehtävät

Tähän asti elementtimenetelmällä on ratkaistu tasapainotiloja. Kun
mukaan tulee aika, tarvitaan yksi uusi matriisi: **massamatriisi**,
joka kertoo, miten hitaus tai lämpökapasiteetti jakautuu solmuille.
Sen avulla saadaan kaksi asiaa. Rakenteen ominaistaajuudet ja
-muodot ratkeavat suoraan ominaisarvotehtävänä, ilman luvun 5
aikasimulaatiota ja spektriä. Ja lämpenemisen tai värähtelyn
aikakehitys lasketaan samoilla aikaintegroijilla kuin luvuissa 4 ja 5,
nyt mielivaltaisessa geometriassa.

## Massamatriisi

Aaltoyhtälön $\rho\,u_{tt} = \nabla\cdot(T\nabla u)$ heikko muoto saa
vasemmalle puolelleen termin $\int \rho\,u_{tt}\,v\,dA$. Kun siihen
sijoitetaan kantafunktiot, tulee yhtälöryhmä

$$M\,\ddot{\mathbf u} + K\,\mathbf u = \mathbf f,
  \qquad M_{ij} = \int \rho\,\varphi_i\,\varphi_j\,dA.$$

Tämä on sama yhtälö kuin jousi–massa-värähtelijällä, mutta matriiseilla.
Lämpöyhtälö antaa vastaavasti $M\dot{\mathbf u} + K\mathbf u =
\mathbf f$, jossa $M$:n kertoimena on $\rho c$.

Yhdessä ulottuvuudessa lineaarisen elementin massamatriisi on

$$M^e = \frac{\rho h}{6}\begin{pmatrix} 2 & 1 \\ 1 & 2 \end{pmatrix}.$$

Tämä integraalista laskettu muoto on **konsistentti massamatriisi**.
Sen sivualkiot kytkevät naapurisolmujen kiihtyvyydet toisiinsa.
Vaihtoehto on **keskitetty massamatriisi**, jossa jokaisen rivin summa
siirretään lävistäjälle: elementin massa jaetaan puoliksi sen
solmuille, kuin ne olisivat pistemassoja. Keskitetty matriisi on
lävistäjämatriisi, ja sen kääntäminen on pelkkä jakolasku.

```{.python tiedosto="esimerkit/10-taajuudet.py" osa="matriisit"}
```

## Ominaistaajuudet ominaisarvotehtävänä

Vapaa värähtely $\mathbf u(t) = \mathbf v \cos\omega t$ toteuttaa
yhtälön $M\ddot{\mathbf u} + K\mathbf u = 0$ täsmälleen silloin, kun

$$K\,\mathbf v = \omega^2 M\,\mathbf v.$$

Tämä on **yleistetty ominaisarvotehtävä**. Ominaisarvot ovat
kulmataajuuksien neliöt ja ominaisvektorit värähtelymuodot. Kielelle,
jonka päät ovat kiinni, tarkat arvot ovat $\omega_k = k\pi c/L$, joten
tulosta voi verrata.

```{.python tiedosto="esimerkit/10-taajuudet.py" osa="moodit"}
```

```{.tuloste tiedosto="esimerkit/10-taajuudet.odotettu" rivit="1-7"}
```

Kymmenellä elementillä alin taajuus on puolen prosentin päässä
tarkasta, kolmas neljän prosentin ja ylin kymmeniä prosentteja.
Verkko pystyy esittämään vain muotoja, joiden aallonpituus on monta
elementtiä. Sääntö on sama kuin luvussa 5: noin kymmenen elementtiä
aallonpituutta kohden. Verkon ylimmät ominaistaajuudet ovat verkon
ominaisuuksia, eivät rakenteen.

Massamatriisin muoto määrää virheen suunnan. Konsistentti matriisi
yliarvioi taajuudet, ja keskitetty aliarvioi alimpia taajuuksia
suunnilleen yhtä paljon. Konsistentin matriisin yliarvio ei ole
sattumaa: Galerkinin menetelmä rajoittaa rakenteen liikkeen
kantafunktioiden muotoihin, ja rajoitettu rakenne on aina jäykempi
kuin vapaa.

```{.python tiedosto="esimerkit/10-taajuudet.py" osa="kertaluku"}
```

```{.tuloste tiedosto="esimerkit/10-taajuudet.odotettu" alkaen="alimman"}
```

Alimman taajuuden virhe pienenee toisessa kertaluvussa. Oikeanpuoleiset
sarakkeet kertovat aikaintegroinnista: luvun 5 eksplisiittinen kaavio
on stabiili, kun $\Delta t < 2/\omega_{\max}$. Keskitetyllä massalla
suurin taajuus lähestyy arvoa $2c/h$, ja ehdosta tulee CFL-ehto
$\Delta t < h/c$. Konsistentilla massalla suurin taajuus lähestyy arvoa
$\sqrt{12}\,c/h$, joten sallittu askel on 42 prosenttia lyhyempi, ja
jokaisella askeleella pitäisi lisäksi ratkaista yhtälöryhmä.
Eksplisiittisessä dynamiikassa, esimerkiksi törmäyssimuloinnissa,
käytetään siksi keskitettyä massaa.

## Kalvon muodot kirjastolla

Kahdessa ulottuvuudessa matriisit ovat suuria ja harvoja, eikä kaikkia
ominaisarvoja voi eikä tarvitse laskea. SciPyn `eigsh` laskee muutaman
ominaisarvon Lanczosin menetelmällä. Alimmat arvot ovat lähinnä nollaa,
ja ne löytyvät nopeimmin **siirretyllä käänteisiteraatiolla**
(`sigma=0`): menetelmä ratkaisee yhtälöryhmiä matriisilla $K$ ja
suppenee kohti ominaisarvoja, jotka ovat lähimpänä siirtoa.

```{.python tiedosto="esimerkit/10-kalvo.py" osa="ominaisarvot"}
```

Neliölle tarkat arvot tunnetaan: $\lambda = \pi^2(m^2 + n^2)$. Luvun
5 taajuudet olivat samat luvut muodossa $f = \sqrt{\lambda}/(2\pi)$.

```{.python tiedosto="esimerkit/10-kalvo.py" osa="nelio"}
```

```{.tuloste tiedosto="esimerkit/10-kalvo.odotettu" rivit="1-5"}
```

Toisen asteen elementeillä neljä alinta arvoa ovat muutaman
sadasosaprosentin tarkkuudella oikein. Toinen ja kolmas ominaisarvo
ovat tarkassa ratkaisussa samat (muodot (1, 2) ja (2, 1)), mutta
lasketut arvot eroavat hieman, koska lävistäjillä jaettu verkko ei ole
symmetrinen akselien vaihdon suhteen. Verkko voi siis rikkoa
symmetrian, joka geometriassa on.

L-alueelle ei ole kaavaa, mutta sen ominaisarvot on laskettu
kirjallisuudessa hyvin tarkasti, ja se on yksi alan
vakiovertailutehtävistä.

```{.python tiedosto="esimerkit/10-kalvo.py" osa="l-alue"}
```

```{.tuloste tiedosto="esimerkit/10-kalvo.odotettu" alkaen="L-alue"}
```

![L-alueen kolme alinta ominaismuotoa. Ensimmäisessä tasa-arvokäyrät
kiertävät nurkan läheltä; kolmas on kolmen neliön
perusmuotojen yhdistelmä.](kuvat/moodit.png){width=95%}

Kaikki viisi arvoa lähestyvät kirjallisuuden lukuja, mutta eri tahtiin.
Kolmas ominaisarvo on täsmälleen $2\pi^2$, ja sen muoto on sileä
sinien tulo: virhe pienenee verkon tihentyessä viidestoistaosaan.
Ensimmäisen muodon gradientti on nurkassa singulaarinen, ja sen virhe
pienenee vain alle puoleen. Sama alue, sama verkko ja sama elementti,
mutta eri muodot suppenevat eri nopeudella sen mukaan, kuinka sileitä
ne ovat.

Kirjallisuusarvoon vertaaminen on tarkistuksen kolmas laji
analyyttisen ratkaisun ja oman vertailutoteutuksen rinnalla. Alan
vakiotehtäville on julkaistu viitearvoja juuri tätä varten.

## Lämpeneminen ajassa

Luvun 7 levy lämmittimineen laitetaan nyt päälle huoneenlämpöisenä.
Yhtälöryhmä $M\dot{\mathbf T} + A\mathbf T = \mathbf b$ ratkaistaan
implisiittisellä Eulerilla, kuten luvussa 4:

$$(M + \Delta t\,A)\,\mathbf T^{n+1} = M\,\mathbf T^n + \Delta t\,\mathbf b.$$

Matriisit kootaan luvun 7 kirjastolla. $A$ sisältää johtumisen ja
konvektioreunan.

```{.python tiedosto="esimerkit/10-lampo.py" osa="kokoaminen"}
```

Vasemman puolen matriisi ei muutu askeleesta toiseen, joten se
hajotetaan kerran, ja jokainen askel on kaksi kolmiomatriisin
ratkaisua.

```{.python tiedosto="esimerkit/10-lampo.py" osa="aika"}
```

```{.tuloste tiedosto="esimerkit/10-lampo.odotettu"}
```

![Levyn lämpeneminen. Keskilämpötila seuraa yhden lämpötilan mallia,
ja kuumin kohta on koko ajan alle asteen sen
yläpuolella.](kuvat/lampeneminen.png){width=66%}

Energiatase toteutuu jokaisella askeleella pyöristystarkkuudella:
lämmittimestä tullut energia miinus konvektiolla poistunut on levyyn
varastoitunut. Implisiittinen Euler ja konsistentti massamatriisi
säilyttävät taseen tarkasti, vaikka itse lämpötilat ovat
likiarvoja.

Taulukon kolmas sarake on yhden lämpötilan malli, jonka aikavakio
on $\rho c V/(hA)$, tässä 81 minuuttia. Se osuu alle puolen asteen
päähän koko mallin keskilämpötilasta. Biot'n luku on 0,025, joten tulos
on luvun 4 nyrkkisäännön mukainen: levyn keskilämpötilan ennustamiseen
ei olisi tarvittu elementtimallia. Sitä tarvitaan, jos kysytään
kuumimman kohdan lämpötilaa tai lämmittimen sijoittelua.

## Käytännössä

- **Ominaistaajuudet ominaisarvotehtävästä, ei aikasimulaatiosta.**
  Se on nopeampi, tarkempi ja antaa myös muodot. Aikasimulaatio
  tarvitaan, kun kiinnostaa vaste tiettyyn kuormaan.
- **Luota vain alimpiin muotoihin.** Nyrkkisääntönä luotettavia ovat
  muodot, joiden puoliaallolla on vähintään viisi elementtiä. Tarkista
  tihentämällä: jos taajuus muuttuu yli prosentin, verkko on liian
  harva sille muodolle.
- **Konsistentti massa implisiittiseen, keskitetty eksplisiittiseen.**
  Implisiittisessä menetelmässä yhtälöryhmä ratkaistaan joka
  tapauksessa, ja konsistentti massa on tarkempi. Eksplisiittisessä
  lävistäjämatriisi on koko menetelmän edellytys.
- **Vertaa ominaistaajuutta herätteeseen.** Mitoituksessa kysymys on
  yleensä, osuuko jokin ominaistaajuus koneen käyntitaajuuteen tai
  kuorman taajuuskaistalle. Vastaus vaatii vain muutaman alimman arvon.
- **Jäykän kappaleen muodot ovat nollia.** Tukemattomalla rakenteella
  on nollataajuuksia, jotka vastaavat siirtoja ja kiertoja. Ne ovat
  oikeita tuloksia, mutta siirretty käänteisiteraatio tarvitsee silloin
  nollasta poikkeavan siirron.
- **Hajota kerran, ratkaise monta kertaa.** Vakioaskeleella ja
  lineaarisella mallilla aikasimulaation hinta on yksi hajotelma ja
  askelta kohden takaisinsijoitus.

## Itsearviointi

- Osaat selittää, mistä massamatriisi syntyy, ja erottaa konsistentin
  ja keskitetyn muodon käyttötarkoituksineen.
- Osaat muotoilla ominaisvärähtelyn yleistettynä ominaisarvotehtävänä
  ja ratkaista sen alimmat arvot harvoille matriiseille.
- Osaat arvioida, mitkä lasketuista ominaistaajuuksista ovat
  luotettavia annetulla verkolla.
- Osaat yhdistää suurimman ominaistaajuuden eksplisiittisen
  aikaintegroinnin stabiilisuusrajaan.
- Osaat ratkaista ajasta riippuvan lämpötehtävän elementtimatriiseilla
  ja tarkistaa tuloksen energiataseella.
