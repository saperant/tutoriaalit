# Putki koodina

Toimitusputki kuvataan nykyisin tiedostona, joka on samassa
repositoriossa kuin koodi. Putken muutos kulkee silloin samaa reittiä
kuin mikä tahansa muutos: se katselmoidaan, sen historia säilyy ja
vanha commit rakennetaan sillä putkella, joka sille kuului. Tämä luku
käy läpi putkijärjestelmien yhteiset käsitteet, putken oman
testaamisen, muutoksiin perustuvan testauksen ja välimuistit. Lopuksi
tarkastellaan näiden tutoriaalien omaa putkea.

## Sama putki kuvauskielellä

Luvun 4 viisivaiheinen putki näyttää GitHub Actions -työnkulkuna
tältä. Tiedoston alku kertoo, milloin putki käynnistyy ja millä
oikeuksilla.

```{.yaml tiedosto="esimerkit/luku06/tyonkulku.yml" osa="ehdot"}
```

Loppuosa kuvaa työt ja niiden riippuvuudet.

```{.yaml tiedosto="esimerkit/luku06/tyonkulku.yml" osa="tyot"}
```

Työnkulku on luvun 4 malli toisella syntaksilla. `needs` on
riippuvuus, `matrix` ajaa kolme tarkistusta rinnakkain, ja paketti
tallennetaan kerran ja haetaan käyttöönottotöissä samana tiedostona.
Käyttöönottotyöt ajetaan vain rungon muutoksille.

Kuvauskieli vaihtuu järjestelmästä toiseen, mutta käsitteet ovat
samat. Kun ne tuntee, uuden järjestelmän oppii sen dokumentaatiosta
päivässä.

| Käsite | Tehtävä | GitHub Actions | GitLab CI |
|---------------|-------------------------------|---------------|---------------|
| heräte | mikä käynnistää putken | `on` | `rules`, `workflow` |
| työ | yksikkö, joka ajetaan yhdellä ajokoneella | `jobs` | työ ja `stage` |
| riippuvuus | töiden järjestys | `needs` | `needs`, `stages` |
| ajokone | kone tai kontti, jossa työ ajetaan | `runs-on` | `tags`, `image` |
| artefakti | tiedosto, joka siirtyy työstä toiseen | `upload-artifact` | `artifacts` |
| välimuisti | uudelleenkäytettävä välitulos | `actions/cache` | `cache` |
| ympäristö | käyttöönoton kohde suojauksineen | `environment` | `environment` |
| samanaikaisuus | saman kohteen ajojen järjestys | `concurrency` | `resource_group` |

Jenkins, Azure Pipelines, Buildkite ja muut sopivat samaan taulukkoon.
Erot ovat siinä, kuka ylläpitää ajokoneita, miten laajennukset
jaetaan ja kuinka hyvin järjestelmä sopii yhteen muun
kehitysalustan kanssa.

## Ohut putki

Putkitiedostoon on helppo kirjoittaa pitkiä komentosarjoja. Sillä on
kaksi haittaa: putkea ei voi ajaa omalla koneella, ja logiikka on
sidottu yhden toimittajan kuvauskieleen.

Kestävämpi rakenne on **ohut putki**. Varsinainen työ on repositorion
omissa skripteissä tai rakennusjärjestelmän kohteissa, ja putkitiedosto
vain kutsuu niitä. Esimerkin työnkulussa varsinaiset askelet ovat
`make`-kohteita tai skriptejä. Tästä seuraa kolme etua.

- Kehittäjä ajaa saman komennon paikallisesti ja saa saman tuloksen,
  joten putken virhe on toistettavissa ilman kokeiluja etäkoneella.
- Skriptit ovat tavallista koodia, jota voi testata.
- Putkijärjestelmän vaihtaminen on kymmenien rivien työ.

Putkitiedostoon jää se, mitä vain putkijärjestelmä voi tehdä: herätteet,
oikeudet, ajokoneet, rinnakkaisuus, välimuistit, artefaktit ja
ympäristöjen suojaus.

## Putken testaaminen

Putki on ohjelma, ja siinä on virheitä. Putken virhe on kahdesta syystä
tavallista ikävämpi: sen huomaa vasta ajamalla, ja pahimmillaan se
näyttää vihreää, vaikka ei testaa mitään. Tarkistuksia on neljällä
tasolla.

**Syntaksi ja skeema.** Putkitiedosto tarkistetaan ennen ajamista.
Tämän tutoriaalin testit ajavat esimerkkityönkululle YAML-tarkistimen
ja vertaavat sitä GitHub Actions -työnkulkujen JSON-skeemaan. Väärin
kirjoitettu avain tai väärä sisennys jää kiinni sekunneissa.

**Skriptien testit.** Kun logiikka on skripteissä, sille kirjoitetaan
yksikkötestit kuten muullekin koodille. Luvun 4 putkimallilla on omat
testinsä hakemistossa `esimerkit/testit`: ne tarkistavat muun muassa,
että epäonnistuneen vaiheen seuraajat ohitetaan ja että
riippuvuuskehä hylätään.

**Kokeilu haarassa.** Putken muutos ajetaan yhdistämispyynnössä ennen
kuin se päätyy runkoon. Tämä on harvoja tilanteita, joissa haara on
trunk-pohjaisessakin kehityksessä luonteva: rikkinäinen putki rungossa
pysäyttää kaikki.

**Putki testaa, että se testaa.** Vaarallisin vika on tarkistus, joka
ei voi epäonnistua: testikomento, jonka paluuarvo jää huomiotta, tai
ehto, joka ohittaa testit aina. Tätä vastaan auttaa sama keino kuin
testivetoisessa kehityksessä: uusi tarkistus nähdään ensin punaisena.
Jos putkeen lisätään tyyppitarkistus, kokeillaan tahallisella
virheellä, että putki todella pysähtyy.

Putken tiedostot ansaitsevat tavallista tarkemman katselmoinnin, koska
putkella on pääsy tuotantoon ja salaisuuksiin. Esimerkkityönkulun
`permissions` rajaa oikeudet lukemiseen. Putken suojaamista
käsittelee *Tietoturva kehitystyössä*.

## Muutoksiin perustuva testaus

Kun repositorio kasvaa, kaiken testaaminen jokaisella muutoksella käy
hitaaksi. Tavallisin lääke on testata vain se, mihin muutos voi
vaikuttaa. Se edellyttää tietoa riippuvuuksista: jos paketti A
käyttää pakettia B, B:n muutos vaatii myös A:n testit.

```{.python tiedosto="esimerkit/luku06/muuttuneet.py" osa="valinta"}
```

```{.tuloste tiedosto="esimerkit/luku06/muuttuneet.odotettu"}
```

Raporttien muutos testaa yhden paketin viidestä. Laskennan muutos
testaa neljä, koska kolme muuta pakettia käyttää sitä suoraan tai
välillisesti. Yhteisen työkalun muutos testaa kaiken, koska sen
vaikutusta ei voi päätellä.

Menetelmän turvallisuus riippuu kokonaan riippuvuustiedon
oikeellisuudesta. Kolme asiaa kannattaa varmistaa.

- **Epävarmassa tapauksessa testataan kaikki.** Tuntematon polku,
  rakennusjärjestelmän muutos tai putken oma muutos laukaisee täyden
  ajon. Liian laaja testaus maksaa aikaa, liian suppea päästää vian
  läpi.
- **Riippuvuudet johdetaan, jos mahdollista.** Käsin ylläpidetty
  luettelo vanhenee. Rakennusjärjestelmät, kuten Bazel, tuntevat
  riippuvuudet tiedostotasolla ja laskevat vaikutusalueen itse.
- **Täysi ajo tehdään silti säännöllisesti.** Yöllinen tai viikoittainen
  ajo kaikelle havaitsee viat, jotka valinta ohitti, ja ympäristön
  muutokset, jotka eivät näy missään commitissa.

Tulosteen viimeinen tapaus kannattaa huomata: pelkän dokumentaation
muutos ei testaa mitään. Se on oikein vain, jos dokumentaatiosta ei
rakenneta mitään, mikä voi hajota.

## Välimuistit

Välimuisti säästää työn, jonka tulos tiedetään jo: ladatut
riippuvuudet, käännetyt välitulokset, konttikuvan kerrokset. Oikein
toimiva välimuisti perustuu yhteen sääntöön: **avain lasketaan kaikesta,
mistä tulos riippuu.**

Riippuvuuksien välimuistin avain on lukitustiedoston tiiviste. Kun
lukitustiedosto muuttuu, avain muuttuu, ja riippuvuudet haetaan
uudelleen. Konttikuvan kerroksen avain on rakennusohjeen rivi ja
kaikki sitä edeltävät kerrokset (ks. *Kontit ja
pilvi-infrastruktuuri*).

Välimuistin kaksi vikaa ovat erihintaiset.

| Vika | Syy | Seuraus |
|-----------------|-------------------------------|--------------------------|
| turha huti | avaimessa on jotain, mistä tulos ei riipu (esimerkiksi päivämäärä) | työ tehdään uudelleen: hidasta mutta oikein |
| väärä osuma | avaimesta puuttuu jotain, mistä tulos riippuu | käytetään vanhentunutta tulosta: nopeaa mutta väärin |

Väärä osuma on vakava, koska se on näkymätön. Putki on vihreä, mutta
se testasi vanhaa tulosta. Siksi välimuistin tulee olla *optimointi,
jonka voi poistaa*: putken on tuotettava sama tulos tyhjällä
välimuistilla, ja tämä tarkistetaan ajamalla putki ajoittain ilman
sitä.

Välimuisti ja artefakti kannattaa pitää käsitteinä erillään. Artefakti
on putken tuotos, jota myöhemmät vaiheet tarvitsevat ja jonka pitää
säilyä. Välimuisti on nopeutus, jonka saa hävittää milloin tahansa.

## Tapaus: tämän aineiston putki

Nämä tutoriaalit rakennetaan ja julkaistaan putkella, joka on
repositorion tiedostossa `.github/workflows/tutoriaalit.yml`. Se on
hyvä tapaus siksi, että se on pieni, oikeassa käytössä ja sisältää
useimmat tämän luvun asiat, myös kompromissit.

**Asetelma.** Repositoriossa on noin sata toisistaan riippumatonta
tutoriaalipakettia. Jokaisella on omat esimerkkinsä, jotka testataan
(`make testaa`), ja PDF, joka ladotaan (`make pdf`). Yhteistä ovat
hakemisto `yhteiset` (latomisen suodattimet ja testityökalut), juuren
`Makefile` ja itse putki. Kehitys on trunk-pohjaista: muutokset
tehdään suoraan päähaaraan, ja jokainen onnistunut rungon ajo julkaisee
sivuston.

```{.dot otsikko="Tutoriaalien putki: neljä työtä, joista julkaisu ajetaan vain rungon muutoksille"}
digraph {
  rankdir=LR; nodesep=0.3; ranksep=0.45;
  pv [label="PDF-\nvälimuisti", shape=cylinder];
  { node [group=p]; m [label="muutokset\n(mitä testataan)"];
    t [label="testaa-ja-rakenna\n(PDF:t, testit, sivusto)"];
    j [label="julkaise\n(sivusto)"]; }
  k [label="kehityskontti\n(matriisi)"];
  pv -> t [dir=both, style=dashed];
  m -> t;
  t -> j [label="vain runko"];
  m -> k;
}
```

**Mitä testataan.** Työ `muutokset` kysyy putkijärjestelmältä
viimeisimmän *onnistuneen* rungon ajon commitin ja vertaa nykyistä
tilaa siihen. Apuohjelma `yhteiset/ci.py` päättelee muuttuneista
poluista testattavat paketit samalla periaatteella kuin edellä:

- paketin oman hakemiston muutos testaa sen paketin
- hakemiston `yhteiset`, juuren `Makefile`n, putken tai kehityskonttien
  yhteisen kuvan muutos testaa kaiken
- taitopuu ja sivusto testataan aina, koska ne kokoavat kaikki paketit
- jos vertailukohtaa ei ole, testataan kaikki.

Vertailukohta on viimeisin onnistunut ajo eikä edellinen commit. Ero on
olennainen: jos edellinen ajo epäonnistui, sen muutokset eivät ole
vielä läpäisseet testejä, ja ne on testattava uudelleen yhdessä uusien
kanssa. Paketit ovat toisistaan riippumattomia, joten riippuvuusverkko
on yksinkertainen: jokainen riippuu vain yhteisistä tiedostoista.

Yhdistämispyynnöt, käsin käynnistetyt ajot ja viikoittainen ajastettu
ajo testaavat kaiken. Viikkoajo on olemassa ympäristön vuoksi: osa
työkaluista asennetaan käyttöjärjestelmän paketteina ilman kiinnitettyä
versiota, joten ympäristö voi muuttua, vaikka repositorio ei muutu.

**PDF-välimuisti.** Kaikkien PDF-tiedostojen latominen on putken hitain
osa, ja sivusto tarvitsee ne kaikki joka kerta. Putki tallentaa siksi
valmiit PDF:t välimuistiin. Paketin avain on Gitin puutiiviste kolmesta
asiasta: paketin omasta hakemistosta, hakemistosta `yhteiset` ja
taitopuun tiedostosta, josta PDF:n väri ja alueen nimi tulevat. Jos
jokin näistä muuttuu, avain muuttuu ja PDF ladotaan uudelleen.
Muuttumattoman paketin PDF kopioidaan välimuistista ja merkitään
tuoreeksi, jolloin `make` ei rakenna sitä.

Avain on sisältöön perustuva, ei aikaan. Se noudattaa edellisen osion
sääntöä: mukana on kaikki, mistä tulos riippuu ja minkä repositorio
tuntee. Mukana ei ole ajokoneen työkaluversioita, kuten latomisohjelmaa.
Se on tietoinen rajaus, jonka hinta on, että työkalun päivitys ei
yksin rakenna PDF:iä uudelleen.

**Rakenna kerran.** Sivusto kootaan testityössä ja tallennetaan
artefaktiksi. Julkaisutyö ei rakenna mitään, vaan ottaa käyttöön saman
artefaktin. Julkaisutyöllä on myös eri oikeudet: vain se saa
kirjoittaa sivustolle, ja muu putki toimii lukuoikeuksin.

**Samanaikaisuus.** Saman haaran ajot suoritetaan peräkkäin. Käynnissä
olevaa ajoa ei keskeytetä, ja jonoon jää vain uusin odottava ajo.
Valinnalla on kaksi perustetta. Vanhempi ajo ei voi julkaista sivustoa
uudemman päälle, ja tiheät muutokset eivät peruuta jokaista ajoa
kesken, jolloin mikään ei valmistuisi. Luvun alun esimerkkityönkulku
tekee toisen valinnan yhdistämispyynnöille: niissä vanha ajo
perutaan, koska vain uusimman tulos kiinnostaa.

**Kehityskontit.** Jokaisella tutoriaalilla on oma kehityskontti,
jossa lukija voi ajaa esimerkit. Työ `kehityskontti` rakentaa
muuttuneiden pakettien kontit ja ajaa niiden testit kontin sisällä,
jolloin varmistuu, että lukijan ympäristö ja putken ympäristö
tuottavat saman tuloksen. Työ on matriisi, jonka alkiot putki laskee
ajon aikana, ja yhden kontin epäonnistuminen ei keskeytä muita.
Konttikuvien kerrokset tallennetaan välimuistiin.

**Kompromissit.** Putki ei ole malliesimerkki joka suhteessa, ja
puutteet ovat opettavaisia.

- Testit ja PDF:t ovat yhdessä pitkässä työssä, jonka aikaraja on
  kaksi ja puoli tuntia. Täysi ajo on kaukana kymmenen minuutin
  tavoitteesta. Muutoksiin perustuva testaus pitää tavallisen ajon
  lyhyenä, mutta yhteisen tiedoston muutos maksaa täyden hinnan.
- Työkalut asennetaan jokaisessa ajossa. Valmis ajokoneen kuva olisi
  nopeampi ja toistettavampi, mutta se olisi uusi ylläpidettävä asia.
- Suoraan runkoon yhdistäminen tarkoittaa, että runko voi olla
  punainen. Sivusto julkaistaan vain vihreästä ajosta, joten lukijat
  eivät näe rikkinäistä tilaa, ja korjaus tehdään heti.
- Testattavien pakettien valinta nojaa siihen, että paketit ovat
  riippumattomia. Jos paketti alkaisi käyttää toisen paketin
  tiedostoja, valinta pitäisi korjata, eikä mikään tarkistus varoita
  siitä.

## Käytännössä

- Pidä putkitiedosto ohuena: työ skripteihin, joita voi ajaa ja
  testata paikallisesti.
- Tarkista putkitiedoston syntaksi ja skeema automaattisesti.
- Kun lisäät tarkistuksen, näe se ensin punaisena.
- Jos testaat vain muuttuneet osat, testaa epävarmassa tapauksessa
  kaikki ja aja täysi testi säännöllisesti.
- Laske välimuistin avain sisällöstä ja varmista, että putki toimii
  myös tyhjällä välimuistilla.
- Päätä samanaikaisten ajojen käsittely tietoisesti: perutaanko vanha
  vai odottaako uusi.

## Itsearviointi

- Osaat nimetä putkijärjestelmien yhteiset käsitteet ja tunnistaa ne
  vieraan järjestelmän kuvauskielestä.
- Osaat perustella ohuen putken ja kertoa, mikä kuuluu
  putkitiedostoon ja mikä skripteihin.
- Osaat kuvata neljä tapaa testata putkea itseään.
- Osaat päätellä riippuvuuksista, mitkä osat muutos vaatii
  testattavaksi, ja kertoa menetelmän riskit.
- Osaat muodostaa välimuistin avaimen ja selittää, miksi väärä osuma
  on pahempi kuin turha huti.
- Osaat selittää, miksi muutosten vertailukohta on viimeisin
  onnistunut ajo eikä edellinen commit.
