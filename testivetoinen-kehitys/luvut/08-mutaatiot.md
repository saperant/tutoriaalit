# Kattavuus ja mutaatiotestaus

Edellisissä luvuissa testisarjan hyvyys mitattiin käsin tehdyllä
viallisella toteutuksella: hyvä sarja epäonnistui sillä, huono ei. Tässä
luvussa sama mittaus yleistetään. Ensin katsotaan, miksi tavallisin
mittari, kattavuus, ei vastaa kysymykseen, ja sitten annetaan virheiden
tekeminen koneelle.

## Mitä kattavuus mittaa

**Kattavuus** (*coverage*) kertoo, mikä osa koodista suoritettiin
testien aikana. **Rivikattavuus** laskee suoritetut lauseet,
**haarakattavuus** lisäksi sen, kulkiko jokainen ehto sekä toteen että
epätoteen. Mittaamisen työkalut esitellään taidossa
*Käännösjärjestelmät, testaus ja CI*; tässä kiinnostaa, mitä luvusta voi
päätellä.

Testattavana on luvun 4 toimitusmaksu ja pieni lisäfunktio, joka
vähentää maksusta hyvityksen:

```{.python tiedosto="esimerkit/08-mutaatiot/toimitus.py" osa="veloitus"}
```

Ensimmäinen testisarja on kirjoitettu kattavuusluku mielessä:

```{.python tiedosto="esimerkit/08-mutaatiot/test_heikko.py" osa="heikko"}
```

Neljä testiä suorittaa jokaisen rivin ja jokaisen haaran molempiin
suuntiin. Kattavuus on sata prosenttia. Sarjassa on silti kaksi
heikkoutta, joita kattavuus ei näe:

- Yksikään arvo ei ole rajalla. Jokainen vertailuoperaattori voisi olla
  väärin, kuten luvussa 4 nähtiin.
- Viimeinen väite `> 0` hyväksyy minkä tahansa positiivisen luvun.
  Rivi suoritetaan, mutta sen tulosta ei tarkisteta.

Kattavuus mittaa, mitä testit **suorittavat**, ei sitä, mitä ne
**tarkistavat**. Ääritapaus on testi, joka kutsuu koodia ilman
ainuttakaan väitettä: kattavuus nousee, eikä mikään virhe jää kiinni.

Kattavuudesta on silti hyötyä, kun sitä luetaan toiseen suuntaan.
*Kattamaton* rivi on varma tieto: sitä ei testaa mikään. Katettu rivi
kertoo vain, että testaaminen on mahdollista.

## Mutaatiotestauksen idea

**Mutaatiotestaus** kysyy suoraan sitä, mitä halutaan tietää:
huomaisivatko testit, jos koodissa olisi virhe? Työkalu tekee koodiin
yhden pienen muutoksen, esimerkiksi vaihtaa `<=`:n `<`:ksi, ja ajaa
testit. Muutettu ohjelma on **mutantti**.

- Jos jokin testi epäonnistuu, mutantti **tapettiin**: testit
  huomasivat muutoksen.
- Jos kaikki testit menevät läpi, mutantti **jäi henkiin**: koodin
  käytös muuttui, eikä yksikään testi välittänyt.

**Mutaatiopisteet** (*mutation score*) on tapettujen osuus kaikista
mutanteista.

```{.dot otsikko="Jokainen mutantti on yksi koe: huomaavatko testit tämän muutoksen"}
digraph {
  rankdir=LR; ranksep=0.3;
  k [label="Koodi"];
  m [label="Mutantti\nyksi muutos"];
  t [label="Aja testit"];
  x [label="Tapettu\ntesti epäonnistui", fillcolor="#CDE8C5"];
  h [label="Hengissä\nkaikki läpi", fillcolor="#F4C7C3"];
  k -> m [label="operaattori"];
  m -> t;
  t -> x;
  t -> h;
}
```

Menetelmä nojaa kahteen oletukseen, jotka DeMillo, Lipton ja Sayward
esittivät vuonna 1978. Ensimmäinen on, että pätevän ohjelmoijan virheet
ovat pieniä poikkeamia oikeasta ohjelmasta. Toinen on **kytkentäilmiö**:
testit, jotka löytävät yksinkertaiset virheet, löytävät useimmiten myös
niiden yhdistelmät. Kumpikin on kokemusperäinen havainto, ei lause, ja
tutkimus tukee niitä kohtuullisesti (Just ym. 2014 vertasivat
mutantteja oikeisiin vikoihin).

## Oma mutaattori

Periaate mahtuu reiluun sataan riviin. Pythonin `ast`-moduuli jäsentää
lähdekoodin puuksi, jota voi muokata ja muuttaa takaisin koodiksi
(taito *Kääntäjätekniikka* selittää syntaksipuut). Mutaattorissa on
neljä **mutaatio-operaattoria**: vertailun vaihto, laskutoimituksen
vaihto, loogisen operaattorin vaihto ja kokonaislukuvakion kasvatus
yhdellä.

```{.python tiedosto="esimerkit/08-mutaatiot/mutaattori.py" osa="operaattorit"}
```

`Muuntaja` kulkee puun läpi ja laskee paikat, joissa jonkin
operaattorin voisi soveltaa. Se tekee muutoksen vain paikkaan numero
`kohde`, joten jokaisessa mutantissa on täsmälleen yksi muutos:

```{.python tiedosto="esimerkit/08-mutaatiot/mutaattori.py" osa="muuntaja"}
```

Mutantit tuotetaan kasvattamalla kohdetta, kunnes paikat loppuvat.
Jokainen mutantti kirjoitetaan väliaikaiseen hakemistoon testien
viereen, ja testit ajetaan omassa prosessissaan:

```{.python tiedosto="esimerkit/08-mutaatiot/mutaattori.py" osa="mutantit"}
```

Valitsin `-x` pysäyttää ajon ensimmäiseen epäonnistumiseen: mutantin
tappamiseen riittää yksi testi.

## Kaksi testisarjaa, sama kattavuus

Toinen testisarja on kirjoitettu lukujen 4 ja 5 tekniikoilla. Siinä on
samat tapaukset sekä rajat ja täsmälliset odotusarvot. Kelvottoman
painon testi on jätetty otteesta pois:

```{.python tiedosto="esimerkit/08-mutaatiot/test_vahva.py" osa="vahva"}
```

Molemmille sarjoille mitataan kattavuus ja ajetaan mutaattori:

```{.tuloste tiedosto="esimerkit/08-mutaatiot/odotettu"}
```

Kattavuus on kummallakin sama, mutta ensimmäinen sarja tappaa
mutanteista alle kolmanneksen. Henkiin jääneiden lista on käytännössä
työlista (rivinumerot viittaavat tiedostoon `toimitus.py`):

- Rivit 3–6 ja 10: jokaista rajavakiota voi siirtää yhdellä kenenkään
  huomaamatta. Rajoilta puuttuvat testit.
- Rivit 10–18: jokaisen vertailun voi vaihtaa tiukasta väljään tai
  päinvastoin. Sama puute toisesta suunnasta.
- Rivi 28: vähennyslaskun voi vaihtaa yhteenlaskuksi. Väite `> 0` ei
  erota 490:tä 1 490:stä.

Tämä on mutaatiotestauksen varsinainen hyöty. Prosenttiluku kertoo
suunnan, mutta jokainen henkiin jäänyt mutantti on konkreettinen
kysymys: *tämän muutoksen voisi tehdä tuotantokoodiin, eikä mikään
hälyttäisi. Onko se tarkoitus?*

## Ekvivalentti mutantti

Vahvakin sarja jättää yhden mutantin henkiin: rivillä 26 ehto
`hyvitys >= maksu` muuttui muotoon `hyvitys > maksu`. Testiä, joka
tappaisi sen, ei voi kirjoittaa. Kun hyvitys on yhtä suuri kuin maksu,
alkuperäinen koodi palauttaa nollan ensimmäisestä haarasta ja mutantti
laskee toisessa haarassa `maksu - hyvitys`, joka on myös nolla.
Ohjelmat ovat eri näköisiä mutta käyttäytyvät samoin kaikilla syötteillä.

Tällainen on **ekvivalentti mutantti**. Niitä ei voi tunnistaa
automaattisesti yleisessä tapauksessa, koska kahden ohjelman
samanlaisuuden ratkaiseminen on laskennallisesti mahdoton ongelma.
Käytännön seuraukset:

- Sadan prosentin mutaatiopisteet eivät ole järkevä tavoite. Osa
  henkiin jääneistä on ekvivalentteja, ja ne pitää käydä läpi käsin.
- Ekvivalentti mutantti on joskus vihje koodista. Tässä se kertoo, että
  ehdon yhtäsuuruus on tarpeeton: `max(0, maksu - hyvitys)` tekisi
  saman ilman haaraa.

## Mitä mutaatiotestaus maksaa

Jokainen mutantti vaatii testiajon. Esimerkin kolmenkymmenen rivin
moduulista syntyi 19 mutanttia neljällä operaattorilla; oikeat työkalut
käyttävät kymmeniä operaattoreita ja tuottavat tuhansia mutantteja
keskikokoisesta kirjastosta. Jos testisarja kestää minuutin, ajo kestää
päiviä.

Työkalut vähentävät työtä usealla tavalla:

- **Vain kattavat testit.** Mutantille ajetaan vain ne testit, jotka
  suorittavat muutetun rivin. Kattamattoman rivin mutanttia ei ajeta
  lainkaan, koska se jää varmasti henkiin.
- **Vain muuttunut koodi.** Katselmoinnissa mutatoidaan vain muutoksen
  koskemat rivit. Näin Google raportoi käyttävänsä mutaatiotestausta
  (Petrović ja Ivanković 2018): henkiin jääneet mutantit näytetään
  katselmoijalle huomautuksina.
- **Otanta ja operaattorien valinta.** Osa mutanteista riittää suunnan
  näkemiseen, ja harvoin hyödylliset operaattorit jätetään pois.
- **Aikakatkaisu.** Mutantti voi tehdä silmukasta päättymättömän.
  Aikarajan ylitys lasketaan tapoksi.

Valmiita työkaluja ovat Pythonin mutmut ja cosmic-ray, Javan PIT,
JavaScriptin ja C#:n Stryker sekä Rustin cargo-mutants. Ne toimivat
kuten luvun mutaattori, mutta nopeammin ja useammilla operaattoreilla.

Mutaatiotestaus kannattaa kohdistaa koodiin, jossa virhe on kallis ja
logiikkaa on paljon: hinnoittelu, oikeuksien tarkistus, jäsentimet ja
protokollat. Liimakoodille ja käyttöliittymälle se tuottaa lähinnä
melua.

## Käytännössä

- **Lue kattavuusraportista aukot, älä prosenttia.** Kattamaton haara
  on tieto. Korkea prosentti ei ole.
- **Älä aseta kattavuudelle tiukkaa tavoitelukua.** Kun mittarista
  tulee tavoite, syntyy testejä, jotka suorittavat koodia tarkistamatta
  mitään. Kohtuullinen alaraja estää romahduksen; loppu on
  katselmoinnin asia.
- **Aja mutaatiotestaus ensin yhdelle tärkeälle moduulille.** Tulos
  kertoo nopeasti, millaisia aukkoja testeissä tyypillisesti on.
- **Korjaa testit, älä pisteitä.** Henkiin jäänyt mutantti rajalla
  tarkoittaa puuttuvaa rajatestiä. Kirjoita se määrittelystä, älä
  mutantista.
- **Merkitse ekvivalentit mutantit.** Työkaluissa on tapa ohittaa
  tietty rivi tai mutantti. Perustele ohitus kommentissa.
- **Ominaisuustestit tappavat mutantteja tehokkaasti.** Edestakaisuus-
  ja oraakkelitesti tarkistavat tuloksen kaikilla syötteillä, myös
  rajoilla, joita kukaan ei luetellut.

## Itsearviointi

- Osaat selittää, mitä rivi- ja haarakattavuus mittaavat, ja antaa
  esimerkin testistä, joka nostaa kattavuutta löytämättä virheitä.
- Osaat kuvata mutaatiotestauksen kierroksen ja käsitteet mutantti,
  tapettu, henkiin jäänyt ja mutaatiopisteet.
- Osaat lukea henkiin jääneiden mutanttien listan ja päätellä, mikä
  testi puuttuu.
- Osaat tunnistaa ekvivalentin mutantin ja perustella, miksi sitä ei
  voi tappaa.
- Osaat arvioida, mihin koodiin mutaatiotestaus kannattaa kohdistaa ja
  miten sen kustannusta rajataan.
