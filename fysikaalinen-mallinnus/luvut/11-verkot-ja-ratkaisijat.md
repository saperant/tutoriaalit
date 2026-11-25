# Verkot ja ratkaisijat

Käytännön laskentatyössä suurin osa ajasta ei kulu yhtälöihin vaan
verkkoon: sen tekemiseen, korjaamiseen ja tihentämiseen. Verkko määrää
sekä tarkkuuden että laskennan hinnan. Tässä luvussa katsotaan kolme
asiaa, joiden varassa nuo molemmat ovat: millainen kolmio on huono,
minne solmut kannattaa sijoittaa ja mitä yhtälöryhmän ratkaiseminen
maksaa, kun verkko tihenee.

## Mistä verkko tulee

Tutoriaalin verkot on tehty kolmella tavalla, jotka kattavat
yksinkertaiset tapaukset:

- **Rakenteinen verkko** on säännöllinen ruudukko, jonka solmut
  voidaan numeroida riveittäin (luvun 7 `suorakulmio`). Se on nopea
  tehdä ja käyttää, mutta sopii vain suorakulmaisiin alueisiin.
- **Kuvattu verkko** on rakenteinen verkko parametritasossa, joka
  kuvataan kaarevaan alueeseen (luvun 9 reikälevy). Solmujen jakaumaa
  ohjataan kuvauksella. Tapa toimii, kun alue on topologisesti
  nelikulmio tai jaettavissa sellaisiksi.
- **Tihennetty verkko** saadaan jakamalla karkean verkon kolmioita
  pienemmiksi, kaikkialta tai valikoiden.

Mielivaltaiselle geometrialle tarvitaan **rakenteeton verkko** ja
verkkogeneraattori. Yleisin avoin generaattori on Gmsh, joka lukee
geometrian omasta kuvauskielestään tai CAD-tiedostosta ja kirjoittaa
solmut ja elementit tiedostoon. scikit-fem lukee tiedoston
`meshio`-kirjaston kautta, ja tulos on sama kahden taulukon
tietorakenne kuin kaikissa tämän tutoriaalin verkoissa. Generaattorin
käyttö on oma taitonsa eikä kuulu tähän, mutta sen tuottaman verkon
arviointi kuuluu.

## Kolmion muoto

Elementtimenetelmän virheraja riippuu elementin koosta ja muodosta.
Tavallinen ohje on välttää litteitä kolmioita, mutta ohje on
epätarkka: litteitä kolmioita on kahta lajia, ja vain toinen on
vaarallinen.

Esimerkissä sama Poissonin tehtävä ratkaistaan verkoilla, joissa
ruutuja on vaakasuunnassa kahdeksan ja pystysuunnassa enemmän, joten
kolmiot ovat litteitä. Suorassa verkossa jokaisessa kolmiossa on suora
kulma. Siirretyssä verkossa joka toista solmuriviä on siirretty puoli
ruutua sivulle, jolloin kolmioihin syntyy lähes 180 asteen kulma.
Solmuja on kummassakin yhtä monta.

```{.python tiedosto="esimerkit/11-laatu.py" osa="verkot"}
```

![Kaksi verkkoa, joissa on samat solmumäärät ja yhtä litteät
kolmiot.](kuvat/verkot.png){width=95%}

```{.python tiedosto="esimerkit/11-laatu.py" osa="virhe"}
```

```{.tuloste tiedosto="esimerkit/11-laatu.odotettu"}
```

Suora verkko käyttäytyy odotetusti. Pystysuuntainen tihennys ei auta
enää, kun virheen määrää vaakasuunnan karkea jako, mutta se ei
myöskään haittaa, vaikka pienin kulma on alle kaksi astetta.
Siirretyssä verkossa virhe on viisinkertainen ja **kasvaa**, kun
solmuja lisätään: neljä kertaa tiheämpi verkko antaa lähes kaksi kertaa
suuremman virheen.

Syy on kantafunktion gradientissa. Kun kolmion yksi kulma lähestyy 180
astetta, kärki on melkein vastakkaisella sivullaan, ja pienikin ero
solmuarvoissa tuottaa suuren gradientin sivua vastaan kohtisuoraan
suuntaan. Interpolaation virhe derivaatassa kasvaa rajatta. Pieni
kulma yksinään ei tee samaa, jos suurin kulma pysyy kaukana oikokulmasta
(Babuška ja Aziz, 1976).

Sääntö on siis: **vältä suuria kulmia**. Verkkogeneraattorien
laatumittarit (pienin kulma, sivusuhde, vinous) ovat tämän epäsuoria
mittareita. Litteät, suorakulmaiset elementit ovat hyödyllisiä, kun
ratkaisu muuttuu yhdessä suunnassa paljon nopeammin kuin toisessa,
kuten virtauksen rajakerroksessa.

## Solmut sinne, missä virhe syntyy

Luvussa 7 L-alueen nurkka pudotti kertaluvun arvoon 4/3. Tasainen
tihennys tuhlaa silloin solmuja: virhe syntyy nurkassa, mutta suurin
osa uusista solmuista menee alueille, joissa ratkaisu on sileä.

Singulariteetille $r^{2/3}$ voidaan johtaa, kuinka nopeasti elementtien
pitää pienentyä nurkkaa kohti, jotta virhe jakautuu tasan. Yksi
riittävä sääntö on, että elementin koko on enintään $H\sqrt{r}$,
jossa $r$ on etäisyys nurkasta ja $H$ verkon yleinen koko. Esimerkki
jakaa kolmioita, kunnes sääntö toteutuu.

```{.python tiedosto="esimerkit/11-porrastus.py" osa="tihennys"}
```

Kun kolmio jaetaan, sen naapuriin jäisi solmu keskelle sivua. Tällaista
**roikkuvaa solmua** ei tavallisessa elementtimenetelmässä sallita,
joten kirjasto jakaa naapureitakin sen verran kuin tarvitaan.

```{.python tiedosto="esimerkit/11-porrastus.py" osa="koe"}
```

```{.tuloste tiedosto="esimerkit/11-porrastus.odotettu"}
```

![Vasemmalla porrastettu verkko: kolmiot pienenevät kohti nurkkaa.
Oikealla virhe solmumäärän funktiona. Porrastettu verkko palauttaa
täyden kertaluvun.](kuvat/porrastus.png){width=95%}

Porrastettu verkko palauttaa kertaluvun kahteen. 5854 solmulla sen
virhe on kahdeksasosa siitä, minkä tasainen verkko antaa 12 545
solmulla. Sama tarkkuus tasaisella verkolla vaatisi mitatulla
kertaluvulla noin 300 000 solmua.

Tässä tiedettiin etukäteen, missä singulariteetti on. Yleensä ei
tiedetä, ja silloin käytetään **adaptiivista tihennystä**: ratkaistaan
karkealla verkolla, arvioidaan virhe elementeittäin lasketusta
ratkaisusta (esimerkiksi vuon hypyistä elementtien rajoilla),
jaetaan pahimmat elementit ja toistetaan. Silmukka löytää nurkat,
kuormien reunat ja aineiden rajat itse. Useimmissa kirjastoissa ja
kaupallisissa ohjelmissa se on valmiina, ja scikit-femin
esimerkkikokoelmassa on siitä toteutus.

## Yhtälöryhmän hinta

Diskretointi tuottaa harvan yhtälöryhmän, jonka ratkaisijat ovat
tuttuja taidosta *Numeeriset menetelmät*: suora harva hajotelma ja
liittogradienttimenetelmä. Tässä katsotaan, miten niiden työ kasvaa,
kun verkko tihenee.

```{.python tiedosto="esimerkit/11-ratkaisijat.py" osa="mittaus"}
```

```{.tuloste tiedosto="esimerkit/11-ratkaisijat.odotettu"}
```

Sarake *alkioita* on matriisin nollasta poikkeavien alkioiden määrä.
*Täyttö* kertoo, kuinka moninkertainen määrä niitä on hajotelman
tekijöissä.

**Suora ratkaisija** maksaa hajotelman täyttymisenä: tekijöihin syntyy
nollasta poikkeavia alkioita paikkoihin, joissa alkuperäisessä
matriisissa oli nolla. Luonnollisessa järjestyksessä (solmut
riveittäin) täyttö kasvaa suhteessa ruutujen määrään sivulla, koska
koko kaista lävistäjän ympärillä täyttyy. Täyttöä vähentävä
uudelleenjärjestys pienentää sen 128 ruudun verkolla alle puoleen, ja
ero kasvaa verkon mukana. Järjestys on ratkaisijan oletus, mutta
sen olemassaolo kannattaa tietää: sama matriisi voi olla helppo tai
mahdoton sen mukaan, missä järjestyksessä tuntemattomat eliminoidaan.

**Liittogradienttimenetelmä** ei täytä mitään, mutta sen kierrosmäärä
kaksinkertaistuu, kun hilaväli puolittuu. Syy on ehtoluku: Poissonin
matriisin ehtoluku kasvaa kuten $h^{-2}$, ja liittogradientin
kierrokset kuten ehtoluvun neliöjuuri. Koska tuntemattomiakin on
nelinkertainen määrä, työ kasvaa kahdeksankertaiseksi jokaisella
tihennyksellä. Esiehdostus pienentää ehtolukua. Paras tunnettu
esiehdostin tälle tehtäväluokalle on **monihilamenetelmä**
(*multigrid*), joka ratkaisee virheen eri aallonpituudet eri
tiheyksisillä verkoilla ja pitää kierrosmäärän verkosta riippumattomana.

Nyrkkisääntö: tasotehtävissä suora ratkaisija on yleensä paras
satoihintuhansiin tuntemattomiin asti. Kolmiulotteisissa tehtävissä
täyttyminen kasvaa niin nopeasti, että iteratiivinen ratkaisija hyvällä
esiehdostimella on välttämätön jo paljon aiemmin.

## Käytännössä

- **Katso verkkoa ennen laskentaa.** Piirrä se. Suuret kulmat,
  äkilliset kokoerot vierekkäisten elementtien välillä ja kapeat
  kannakset näkyvät silmällä.
- **Tihennä siellä, missä ratkaisu muuttuu.** Nurkat, reiät, kuormien
  reunat ja aineiden rajat. Muualla karkea verkko riittää.
- **Anna koon muuttua vähitellen.** Vierekkäisten elementtien
  kokosuhde korkeintaan noin kaksi. Äkillinen hyppy heikentää
  tarkkuutta ja matriisin ehtolukua.
- **Tee tihennystutkimus.** Yksikään verkko ei ole "riittävän tiheä"
  ennen kuin tulos on laskettu myös tiheämmällä verkolla ja muutos on
  hyväksyttävän pieni. Luku 12 tekee tästä laskukaavan.
- **Aloita suoralla ratkaisijalla.** Se ei vaadi säätöä eikä jää
  suppenematta. Vaihda iteratiiviseen, kun muisti loppuu.
- **Iteratiivisen ratkaisijan toleranssi on virhelähde.** Jos
  ratkaisija lopetetaan ennen kuin sen virhe on selvästi
  diskretointivirhettä pienempi, tihennystutkimus mittaa ratkaisijaa
  eikä verkkoa.

## Itsearviointi

- Osaat nimetä verkon tekotavat (rakenteinen, kuvattu, tihennetty,
  rakenteeton) ja valita niistä tehtävään sopivan.
- Osaat selittää, miksi suuri kulma heikentää elementtimenetelmän
  tarkkuutta ja pieni kulma yksinään ei.
- Osaat porrastaa verkon kohti singulariteettia ja kertoa, mitä
  adaptiivinen tihennys tekee.
- Osaat arvioida, miten suoran ja iteratiivisen ratkaisijan työ kasvaa
  verkon tihentyessä.
- Osaat kertoa, mistä hajotelman täyttyminen johtuu ja miten
  uudelleenjärjestys vaikuttaa siihen.
