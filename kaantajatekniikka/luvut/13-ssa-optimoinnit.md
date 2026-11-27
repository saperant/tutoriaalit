# Optimointi SSA-muodossa

Luvun 11 arvonumerointi näkee yhden peruslohkon kerrallaan, ja
kuolleen koodin poisto nojaa elävyysanalyysiin. Tässä luvussa samat
kolme ajatusta – vakiot, yhteiset alilausekkeet ja kuollut koodi –
toteutetaan SSA-muodossa, jolloin ne toimivat koko funktion yli.
Passit ovat **harva ehdollinen vakioiden eteneminen**, **globaali
arvonumerointi** ja **kuolleen koodin poisto merkitsemällä**. Ne ovat
käytössä valinnalla `-O2`; oletustaso `-O1` ajaa vain luvun 11 passit,
joten tasoja vertaamalla näkee, mitä SSA-passit lisäävät.

Esimerkkinä on funktio, jossa jokaiselle passille on työtä:

```{.rust tiedosto="esimerkit/naytteet/laske.kide"}
```

Lukija näkee kolme asiaa. Muuttuja `askel` on aina 1, koska se saa
uuden arvon vain, jos se ei ole 1. Tulo `n * k` lasketaan ehdossa ja
uudelleen haarassa. Muuttujaa `kierroksia` kasvatetaan, mutta sitä ei
lueta missään. Luvun 11 passit eivät löydä näistä yhtään, koska
jokainen vaatii tietoa toisesta lohkosta tai silmukan yli. Funktio on
paikallisten passien jälkeen SSA-muodossa tällainen (`--vaihe=ssa`):

```{.tuloste tiedosto="esimerkit/naytteet/ssa-laske.txt"}
```

## Putki

Tasolla `-O2` funktio optimoidaan ensin paikallisilla passeilla ja
viedään sitten SSA-muotoon, optimoidaan siinä ja tuodaan takaisin:

```{.cpp tiedosto="esimerkit/kide/main.cpp" osa="putki"}
```

Kolme viimeistä vaihetta ovat luvun 14 aihe. SSA-passit ajetaan samalla
tavalla kuin paikalliset: kierroksittain, kunnes mikään ei muutu.

```{.cpp tiedosto="esimerkit/kide/ssaopt.cpp" osa="optimoi-ssa"}
```

Uutta on tarkistus jokaisen passin jälkeen. Funktio `tarkista_ssa`
varmistaa SSA-muodon kolme ehtoa: jokaisella rekisterillä on yksi
määrittely, määrittely dominoi jokaista käyttöään (phin argumentin
kohdalla edeltäjälohkon loppua), ja phit ovat lohkon alussa ja
vastaavat lohkon edeltäjiä. Passi, joka rikkoo ehdon, pysäyttää
kääntäjän heti ja nimeää itsensä. Ilman tarkistinta sama virhe
näkyisi vasta käännetyn ohjelman vääränä tuloksena, ja syyllistä
passia pitäisi etsiä tulosteista. LLVM:ssä on vastaava tarkistin
(*IR verifier*), jonka `opt`-työkalun valinta `-verify-each` ajaa
jokaisen passin jälkeen.
Valinta `--vaihe=ssapassit` tulostaa funktion putken jokaisen vaiheen
jälkeen.

## Passien testaaminen

Koko kääntäjän läpi testaaminen ei riitä passille: lähdekielestä on
vaikea saada juuri sitä välikieltä, jonka passin reunatapaus vaatii,
ja aiemmat passit muuttavat syötteen ennen kuin testattava passi näkee
sen. Siksi kääntäjä lukee myös välikielen tekstimuotoa (`.ir`-tiedosto,
sama muoto kuin tulosteissa; lukija on tiedostossa `kide/irluku.cpp`)
ja ajaa sille vain valinnalla `--passit` nimetyt passit. Testi on
välikielitiedosto, jonka ensimmäinen rivi nimeää passit, ja odotettu
tulos sen vieressä:

```{.bash tiedosto="esimerkit/testaa.sh" osa="passitesti"}
```

Jos tiedostossa on `main`-funktio, tulos myös käännetään ja ajetaan.
Jokaisella passilla on vähintään kaksi testiä: yksi, jossa optimointi
tehdään, ja yksi, jossa sitä ei saa tehdä. Jälkimmäinen on tärkeämpi,
sillä liian innokas optimointi tuottaa väärää koodia. SSA-passi
kieltäytyy syötteestä, joka ei ole SSA-muodossa:

```{.tuloste tiedosto="esimerkit/passit/ei-ssa.ir"}
```

```{.tuloste tiedosto="esimerkit/passit/ei-ssa.virhe"}
```

LLVM:n passit testataan samalla tavalla: testi on LLVM IR -tiedosto,
jolle `opt` ajaa nimetyt passit, ja tulosta verrataan tiedostoon
kirjoitettuihin odotuksiin (`FileCheck`).

## Harva ehdollinen vakioiden eteneminen

Vakioiden eteneminen kysyy jokaisesta rekisteristä, onko sen arvo
aina sama vakio. Vastaus on yksi kolmesta, ja vastaukset muodostavat
**hilan** (*lattice*):

```{.cpp tiedosto="esimerkit/kide/ssaopt.cpp" osa="hila"}
```

Analyysi on **optimistinen**: jokainen rekisteri alkaa ylimmältä
tasolta "ei vielä tietoa", ja jokaisen lohkon oletetaan jäävän
suorittamatta, kunnes toisin osoitetaan. Tämä ratkaisee
esimerkkifunktion kehän. Silmukan alun `askel.1` on phi alkuarvosta ja
silmukan lopun arvosta `askel.3`, joka puolestaan riippuu `askel.1`:stä.
Varovainen analyysi, joka olettaa tuntemattoman arvon muuttuvaksi, ei
pääse kehästä sisään. Optimistinen analyysi lukee phistä ensin vain
alkuarvon 1, koska paluukaarta ei ole vielä todettu suoritettavaksi, ja
tarkistaa oletuksen, kun kaari myöhemmin löytyy.

Tieto muuttuu vain alaspäin, ja muutos panee rekisterin työlistalle.
Phi yhdistää vain ne argumentit, joiden kaarta voidaan kulkea:

```{.cpp tiedosto="esimerkit/kide/ssaopt.cpp" osa="aseta"}
```

Muut käskyt arvioidaan operandiensa tiedoista. Haara, jonka ehto
tunnetaan, merkitsee suoritettavaksi vain toisen kaarensa; tästä tulee
nimen sana *ehdollinen*:

```{.cpp tiedosto="esimerkit/kide/ssaopt.cpp" osa="arvioi"}
```

Algoritmissa (Wegman ja Zadeck 1991) on kaksi työlistaa: ohjausvuon
kaaret, jotka on todettu suoritettaviksi, ja rekisterit, joiden tieto
on laskenut. Kun lohkoon tullaan uutta kaarta, sen phit arvioidaan
uudelleen; kun rekisterin tieto laskee, arvioidaan sen käyttäjät:

```{.cpp tiedosto="esimerkit/kide/ssaopt.cpp" osa="sccp"}
```

Sana *harva* (*sparse*) tarkoittaa, että tieto on tallessa kerran
rekisteriä kohden ja kulkee määrittelystä suoraan käyttöihin. Luvun 10
datavuoanalyysi pitää jokaisessa lohkossa joukkoa kaikista
rekistereistä ja kuljettaa sitä lohkosta toiseen. SSA-muodossa
rekisterillä on yksi määrittely, joten sen arvo ei riipu kohdasta, ja
taulukko `arvot_` riittää. Jokainen rekisteri laskee enintään kahdesti
ja jokainen kaari käsitellään kerran, joten työmäärä on lineaarinen
käyttöjen ja kaarten määrässä.

Kun työlistat ovat tyhjät, tulos kirjoitetaan koodiin: vakioksi
todettu määrittely korvataan vakiolla ja tunnetun ehdon haara hypyllä.
Lopuksi `siisti_ssa` poistaa lohkot, joihin ei enää pääse, ja niiden
argumentit phistä. Passin testi on esimerkkifunktion kehä
pelkistettynä:

```{.tuloste tiedosto="esimerkit/passit/vakiot-silmukka.ir"}
```

```{.tuloste tiedosto="esimerkit/passit/vakiot-silmukka.odotettu"}
```

Ehto `ne askel.1, 1` on laskostunut nollaksi, haara on muuttunut
hypyksi, ja sijoitus `askel.2 = 2` on poistunut lohkonsa mukana.
Vakioiksi muuttuneet käskyt ovat yhä paikallaan; niiden poistaminen
on muiden passien työtä. Toisessa testissä
(`passit/vakiot-yhtyma.ir`) on kaksi funktiota, joiden haarat
sijoittavat vakion ja joiden yhtymäkohdassa on
`x = phi [a, L1], [b, L2]`. Funktiossa `f` haarojen vakiot ovat 1 ja
2, joten `x` ei ole vakio eikä optimointia saa tehdä:

```{.tuloste tiedosto="esimerkit/passit/vakiot-yhtyma.odotettu" rivit="10-13"}
```

Funktiossa `g` molemmat haarat sijoittavat ykkösen:

```{.tuloste tiedosto="esimerkit/passit/vakiot-yhtyma.odotettu" rivit="24-27"}
```

## Globaali arvonumerointi

Luvun 11 arvonumerointi piti taulua lausekkeista, jotka lohkossa on
jo laskettu, ja joutui kahdesti varovaiseksi: rekisteriin
kirjoittaminen mitätöi sitä käyttävät rivit, ja lohkon lopussa koko
taulu unohdettiin. SSA-muodossa kumpaakaan syytä ei ole. Rekisteriin
kirjoitetaan kerran, joten avain `mul a, b` tarkoittaa samaa arvoa
kaikkialla, missä `a` ja `b` ovat näkyvissä. Jäljelle jää yksi ehto:
aiemman laskennan on *dominoitava* uutta, jotta sen tulos on varmasti
laskettu. Taulu kuljetetaan siksi dominaattoripuuta pitkin
syvyyshakuna: lohkon lisäämät rivit ovat voimassa sen lapsissa ja
poistetaan, kun lohkosta palataan.

```{.cpp tiedosto="esimerkit/kide/ssaopt.cpp" osa="gvn-lohko"}
```

Jokaisella rekisterillä on **edustaja**, vanhin rekisteri, jolla on
sama arvo. Passi tekee samalla kolme muuta asiaa. Kopion kohde saa
edustajakseen kopion lähteen, joten kopiot etenevät ilman omaa
passiaan. Phi, jonka kaikilla argumenteilla on sama edustaja, on
tarpeeton ja saa sen edustajakseen. Funktio `sievenna` laskostaa
vakiot ja soveltaa luvun 11 algebrallisia sääntöjä, ja se tuntee
vakion, vaikka tämä olisi määritelty toisessa lohkossa.
Vaihdannaisten operaatioiden operandit järjestetään, jotta `mul a, b`
ja `mul b, a` saavat saman avaimen.

```{.tuloste tiedosto="esimerkit/passit/arvot-dominoi.ir"}
```

```{.tuloste tiedosto="esimerkit/passit/arvot-dominoi.odotettu"}
```

Molempien haarojen kertolaskut ovat poistuneet, koska L0 dominoi
kumpaakin. Myös vakio on arvo: lohkon L1 `%4 = 10` on sama kuin L0:n
`%1`, ja edustaja on saanut tulosteessa nimen `$10`. Vakio ladataan
rekisteriin siis kerran koko funktiossa. Hintana rekisteri on varattu
vakiolle määrittelystä viimeiseen käyttöön; luvun 14 mittauksessa
tämä näkyy.

Testissä, jossa optimointia ei saa tehdä, sama tulo lasketaan kahdessa
haarassa ja niiden jälkeen:

```{.tuloste tiedosto="esimerkit/passit/arvot-ei.ir"}
```

Odotettu tulos on sama kuin syöte. Kumpikaan haaroista ei dominoi
lohkoa L3, joten L3 ei voi käyttää `x`:ää eikä `y`:tä: se ei tiedä,
kumpi niistä on laskettu. Tulo on silti L3:ssa aina valmiina jompaa
kumpaa reittiä; tällaisen **osittaisen redundanssin** poisto
(*partial redundancy elimination*) vaatisi phin lisäämistä, eikä Kide
tee sitä. Kutsuja `g(a)` ei yhdistetä, koska kutsu ei ole puhdas
operaatio: `g` voi tulostaa.

## Kuolleen koodin poisto

Luvun 11 passi poisti käskyn, jonka kohde ei ollut elävä. Elävyys ei
kuitenkaan riitä esimerkkifunktion muuttujalle `kierroksia`: sitä
luetaan joka kierroksella, kun sitä kasvatetaan, joten se on elävä
koko silmukan ajan, vaikka mikään tulos ei riipu siitä. SSA-muodossa
kysymys käännetään toisin päin. Lähdetään käskyistä, joilla on
vaikutus funktion ulkopuolelle tai ohjausvuohon (tulostus, kutsu,
paluu, haara), ja merkitään eläviksi niiden lukemien rekisterien
määrittelyt, näiden lukemien rekisterien määrittelyt ja niin edelleen.
Kaikki merkitsemättä jäänyt poistetaan. Menetelmä on sama kuin
roskienkeruun **merkitse ja lakaise** (*mark and sweep*), ja
määrittelyn löytäminen rekisterin nimestä on SSA-muodossa
taulukkohaku:

```{.cpp tiedosto="esimerkit/kide/ssaopt.cpp" osa="kuollut-ssa"}
```

Testissä `k` muodostaa kehän, jonka jäsenet lukevat vain toisiaan:

```{.tuloste tiedosto="esimerkit/passit/kuollut-kierto.ir"}
```

```{.tuloste tiedosto="esimerkit/passit/kuollut-kierto.odotettu"}
```

Vastatestissä kutsun tulosta ei käytetä, mutta kutsu jää, koska se voi
tulostaa; käyttämätön kertolasku `%3` poistuu:

```{.tuloste tiedosto="esimerkit/passit/kuollut-kutsu.odotettu"}
```

Haarat merkitään aina eläviksi, joten passi ei poista silmukkaa, jonka
runko on tyhjentynyt. Sen päätteleminen vaatisi tiedon siitä, mitkä
käskyt riippuvat mistäkin haarasta (*control dependence*), ja lisäksi
varmuuden silmukan päättymisestä.

## Passit yhdessä

Esimerkkifunktio kolmen passin jälkeen (`--vaihe=ssa -O2`):

```{.tuloste tiedosto="esimerkit/naytteet/ssa-laske-O2.txt"}
```

Vakioiden eteneminen totesi `askel`-muuttujan ykköseksi ja poisti
haaran ja sijoituksen. Arvonumerointi korvasi toisen tulon `n * k`
ensimmäisellä (`%9`), sievensi tulon `askel * i` muotoon `i` ja
yhdisti kaikki ykköset rekisteriin `$1` ja nollat rekisteriin `$0`.
Kuolleen koodin poisto vei `kierroksia`-kehän ja haaran mukana
tarpeettomiksi jääneet vertailun osat. Passit tarvitsevat toisiaan:
arvonumerointi ei voi sieventää kertolaskua ennen kuin `askel` on
vakio, ja vertailun osat ovat kuolleita vasta, kun haara on muuttunut
hypyksi.

Lohko L2 on jäänyt tyhjäksi. SSA-passit eivät muuta ohjausvuota muuten
kuin poistamalla saavuttamattomat lohkot, koska jokainen kaaren muutos
vaatisi phien korjaamista. Tyhjät lohkot siivoaa luvun 11 passi, kun
SSA-muodosta on poistuttu.

## Käytännössä

- **Aja tarkistin jokaisen passin jälkeen.** Välikielen invariantit
  (SSA-ehdot, lohkojen rakenne) ovat halpoja tarkistaa, ja rikkoutunut
  invariantti paikantuu passiin eikä käännetyn ohjelman väärään
  tulosteeseen.
- **Testaa passit välikielen tekstimuodosta.** Passin reunatapauksen
  saa kirjoitettua suoraan, eikä testi muutu, kun etuosa tai aiemmat
  passit muuttuvat.
- **Kirjoita jokaiselle optimoinnille testi, jossa sitä ei saa
  tehdä.** Tekemättä jäänyt optimointi on hitaampaa koodia, väärin
  tehty on väärä ohjelma.
- **Optimistinen analyysi löytää enemmän kuin varovainen.** Silmukan
  kehässä kulkeva vakio ja vain itseään ruokkiva laskenta löytyvät
  vain, jos lähdetään oletuksesta "vakio" tai "kuollut" ja
  korjataan sitä.
- **Vakion jakaminen ei ole ilmaista.** Yhteinen arvo säästää käskyn
  mutta pidentää elinväliä; hyöty riippuu siitä, riittävätkö
  rekisterit.

## Itsearviointi

- Osaat selittää vakioiden etenemisen hilan ja sen, miksi
  optimistinen analyysi löytää silmukan kehässä kulkevan vakion.
- Osaat kuvata harvan ehdollisen vakioiden etenemisen kaksi
  työlistaa ja seurata algoritmia pienellä funktiolla.
- Osaat selittää, miksi SSA-muodossa arvonumeroinnin taulua ei
  tarvitse mitätöidä ja miksi aiemman laskennan on dominoitava uutta.
- Osaat poistaa kuolleen koodin merkitsemällä ja kertoa, miksi se
  löytää kehän, jota elävyysanalyysi ei löydä.
- Osaat kirjoittaa optimointipassille testin, jossa optimointi
  tehdään, ja testin, jossa sitä ei saa tehdä.
