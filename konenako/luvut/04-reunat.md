# Reunat, morfologia ja muodot

Kappaleen raja näkyy kuvassa nopeana kirkkauden muutoksena eli
**reunana**. Reunat ovat pieni osa pikseleistä, mutta niissä on suuri osa
kuvan rakenteesta. Tässä luvussa lasketaan gradientti ja reunat,
siistitään binäärikuvia morfologialla ja tulkitaan alueiden muotoja
ääriviivoista.

## Gradientti

Kuvan gradientti $\nabla I = (\partial I/\partial x, \partial I/\partial y)$
osoittaa suuntaan, johon kirkkaus kasvaa nopeimmin, ja sen pituus kertoo
muutoksen voimakkuuden. Reunan suunta on kohtisuorassa gradienttia
vastaan. **Sobel-ydin** laskee derivaatan erotusosamäärällä ja tasoittaa
samalla toisessa suunnassa:

$$
S_x = \begin{pmatrix} -1 & 0 & 1 \\ -2 & 0 & 2 \\ -1 & 0 & 1 \end{pmatrix}
= \begin{pmatrix} 1 \\ 2 \\ 1 \end{pmatrix}
\begin{pmatrix} -1 & 0 & 1 \end{pmatrix}.
$$

Ydin on erottuva: pystysuunnassa tasoitus, vaakasuunnassa derivaatta.
Seuraavassa esimerkissä kuvassa on 30 astetta kierretty neliö, joten
reunojen normaalien pitäisi osoittaa suuntiin 30, 120, 210 ja 300
astetta.

```{.python tiedosto="esimerkit/04-gradientti.py" osa="gradientti"}
```

Derivaatta on negatiivinen, kun kirkkaus laskee. Jos Sobelin tulostyyppi
on `CV_8U`, negatiiviset arvot leikataan nollaan, ja puolet reunoista
katoaa. Tulos lasketaan siksi tyyppiin `CV_32F` tai `CV_16S`.

```{.python tiedosto="esimerkit/04-gradientti.py" osa="uint8"}
```

```{.tuloste tiedosto="esimerkit/04-gradientti.odotettu"}
```

Gradientin suuntien histogrammi on myös monen piirrekuvaajan perusta:
SIFT ja HOG (*histogram of oriented gradients*) kuvaavat ympäristön
gradienttisuuntien jakaumana.

**Laplacen operaattori** $\nabla^2 I = I_{xx} + I_{yy}$ on toinen
derivaatta. Reunan kohdalla se vaihtaa merkkiä, joten reunat ovat sen
nollakohdissa. Laplace on herkkä kohinalle, ja käytännössä sitä
käytetään tasoitetun kuvan kanssa (*Laplacian of Gaussian*) tai
terävyyden mittana: tarkennetussa kuvassa Laplacen varianssi on suuri.

## Canny

**Cannyn reunatunnistin** tuottaa ohuet ja yhtenäiset reunat neljässä
vaiheessa:

1. tasoitus Gaussin suotimella (kohinan vaimennus),
2. gradientin suuruus ja suunta Sobelilla,
3. **ei-maksimien vaimennus**: pikseli säilyy vain, jos sen gradientti on
   suurempi kuin naapureiden gradienttisuunnassa, jolloin reunasta tulee
   yhden pikselin levyinen,
4. **hystereesikynnystys**: yläkynnyksen ylittävät pikselit ovat varmoja
   reunoja, ja alakynnyksen ylittävät hyväksytään, jos ne liittyvät
   varmaan reunaan.

OpenCV:n `Canny` tekee vaiheet 2–4. Tasoitus on tehtävä itse.
Esimerkissä kohinaisesta kuvasta etsitään ympyrän reuna, ja tulosta
arvioidaan kahdella luvulla: **tarkkuus** (*precision*) on oikeiden
osuus löydetyistä reunapikseleistä, ja **saanti** (*recall*) on se osa
oikeasta reunasta, joka löytyi.

```{.python tiedosto="esimerkit/04-canny.py" osa="kuva"}
```

```{.python tiedosto="esimerkit/04-canny.py" osa="arvio"}
```

```{.tuloste tiedosto="esimerkit/04-canny.odotettu"}
```

Ilman tasoitusta kohina tuottaa valtavasti vääriä reunoja (tarkkuus 5 %).
Liian matalat kynnykset tekevät saman tasoitetulle kuvalle. Kun ala- ja
yläkynnys ovat samat (170/170), hystereesiä ei ole, ja heikommat reunan
osat katkeavat: kolmasosa ympyrästä puuttuu. Matalampi alakynnys (60)
täyttää aukot, koska heikot pikselit liittyvät varmoihin. Tavallinen
nyrkkisääntö on yläkynnys kaksi tai kolme kertaa alakynnys.

## Morfologia

Kynnystetty kuva on harvoin siisti. Siinä on yksittäisiä vääriä
pikseleitä ja kappaleissa reikiä. **Morfologiset operaatiot** muokkaavat
binäärikuvaa **rakenne-elementillä**, pienellä muodolla, jota liu'utetaan
kuvan yli.

| Operaatio | Määritelmä | Vaikutus |
|-----------|------------|----------|
| eroosio | pikseli säilyy, jos koko elementti mahtuu kohteeseen | ohentaa, poistaa pienet roskat |
| dilataatio | pikseli tulee kohteeseen, jos elementti osuu kohteeseen | paksuntaa, täyttää pienet reiät |
| avaus | eroosio, sitten dilataatio | poistaa roskat, säilyttää koon |
| sulkeminen | dilataatio, sitten eroosio | täyttää reiät, säilyttää koon |

```{.python tiedosto="esimerkit/04-morfologia.py" osa="kuva"}
```

```{.python tiedosto="esimerkit/04-morfologia.py" osa="operaatiot"}
```

```{.tuloste tiedosto="esimerkit/04-morfologia.odotettu"}
```

Eroosio poistaa roskat mutta laajentaa reikiä ja kutistaa kappaleita.
Dilataatio täyttää reiät mutta yhdistää roskat. Avaus ja sulkeminen
yhdessä tuottavat neljä ehjää suorakaidetta, joiden pinta-ala on
lähellä alkuperäistä. Ellipsin muotoinen elementti pyöristää kulmia
hieman. Kun kappaleiden muoto on tunnettu, elementti valitaan samanlaiseksi.

## Ääriviivat ja muotoanalyysi

`findContours` jäljittää binäärikuvan alueiden rajat pistejonoiksi.
Ääriviivasta saadaan pinta-ala, piiri, ympäröivä suorakaide ja momentit.
**Pyöreys** $4\pi A / P^2$ on ympyrällä 1 ja sitä pienempi muille
muodoille. `approxPolyDP` yksinkertaistaa ääriviivan monikulmioksi
Douglasin–Peuckerin algoritmilla, ja kulmien määrä kertoo muodon.

```{.python tiedosto="esimerkit/04-muodot.py" osa="kuva"}
```

```{.python tiedosto="esimerkit/04-muodot.py" osa="ariviivat"}
```

Pikseleistä mitattu ympyrän piiri on porrastuksen takia hieman liian
pitkä, joten pyöreydeksi tulee 0,89 eikä 1. Raja-arvot asetetaan siksi
väljiksi ja testataan tunnetuilla muodoilla.

**Hu-momentit** ovat seitsemän alueen momenteista laskettua lukua, jotka
eivät muutu siirrossa, skaalauksessa eivätkä kierrossa. Ne ovat
klassinen piirre muotojen vertailuun ja luokitteluun, ja niitä käytetään
luvun 11 luokittelijassa. Arvot vaihtelevat monta kertalukua, joten niistä
käytetään logaritmia.

```{.python tiedosto="esimerkit/04-muodot.py" osa="hu"}
```

```{.tuloste tiedosto="esimerkit/04-muodot.odotettu"}
```

## Käytännössä

- **Tasoita ennen derivointia.** Derivaatta vahvistaa korkeita
  taajuuksia eli kohinaa. Gaussin tasoitus ennen Sobelia tai Cannya on
  oletus.
- **Laske gradientti liukuluvuin.** `CV_32F` tai `CV_16S`, ei koskaan
  `CV_8U`: negatiiviset derivaatat katoavat ilman virheilmoitusta.
- **Säädä Canny tunnetulla kuvalla.** Valitse kynnykset testikuvista,
  joissa oikeat reunat tunnetaan, ja mittaa tarkkuus ja saanti. Pidä
  yläkynnys 2–3 kertaa alakynnys.
- **Siisti maskit morfologialla.** Avaus ennen sulkemista, kun maskissa
  on sekä roskaa että reikiä. Elementin koko valitaan suurimman
  poistettavan roskan mukaan.
- **Käytä muodolle mittakaavasta riippumattomia suureita.** Pyöreys,
  kuvasuhde, täyttöaste ja Hu-momentit toimivat eri kokoisille
  kappaleille. Kiinteät pikselirajat rikkoutuvat, kun kamera siirtyy.

## Itsearviointi

- Osaat laskea kuvan gradientin Sobelilla, selittää sen suunnan ja
  suuruuden ja välttää `uint8`-leikkautumisen.
- Osaat selittää Cannyn neljä vaihetta ja valita kynnykset mittaamalla
  tarkkuuden ja saannin.
- Osaat siistiä binäärikuvan eroosiolla, dilataatiolla, avauksella ja
  sulkemisella ja ennustaa kunkin vaikutuksen.
- Osaat jäljittää ääriviivat ja luokitella muodot kulmien, pyöreyden ja
  Hu-momenttien avulla.
