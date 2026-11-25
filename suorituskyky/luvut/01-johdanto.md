# Johdanto {.runko-johdanto}

Suorituskyky on ominaisuus siinä missä oikeellisuuskin: hidas
käännös katkaisee kehittäjän ajatuksen, hidas palvelin tarvitsee
enemmän koneita, ja hidas sulautettu ohjelma ei ehdi käsitellä
näytettä ennen seuraavaa. Tämä tutoriaali opettaa, miten
suorituskykyä mitataan luotettavasti, miten pullonkaula löydetään ja
miten ohjelma kirjoitetaan laitteiston ehdoilla: välimuistit,
haarautumisen ennustus, vektorikäskyt ja kääntäjän optimoinnit.

## Esitiedot ja rajaus

Esitietoina ovat *Tietokonearkkitehtuuri* ja *Algoritmit*.
Arkkitehtuurin tutoriaali rakensi välimuistin, liukuhihnan ja
haarautumisen ennustimen simulaattorissa; tässä samat ilmiöt
mitataan oikealla suorittimella. Algoritmien tutoriaalista tarvitaan
vaativuusanalyysi: optimointi alkaa aina algoritmista, koska mikään
välimuistitemppu ei pelasta neliöllistä algoritmia, kun syöte kasvaa.
Esimerkit on kirjoitettu C23:lla, koska C näyttää muistin ja käskyjen
hinnan suoraan. C++:n omat kysymykset (siirto, allokaattorit,
mallit) käsitellään taidossa *C++:n suorituskyky* ja näytönohjaimet
taidossa *GPU-laskenta*. Tutoriaali rajautuu yhden ytimen
suorituskykyyn: säikeet, lukot ja rinnakkaiset algoritmit ovat taidossa
*Rinnakkaisohjelmointi*, ja palvelun kapasiteetti ja häntälatenssi
järjestelmän tasolla taidossa *Skaalautuvien järjestelmien
suunnittelu*.

## Mittaa, älä arvaa

Optimointi on kokeellista työtä, ja sen sykli on aina sama:

1. **Mittaa** ohjelma todellisella kuormalla ja kirjaa lähtötaso.
2. **Profiloi**: selvitä, mihin aika kuluu. Pullonkaula on harvoin
   siellä, missä sen arvaa olevan.
3. **Muotoile hypoteesi**: miksi juuri tämä kohta on hidas? Liikaa
   työtä, välimuistihutia, väärin ennustettuja haaroja vai odottamista?
4. **Muuta yhtä asiaa** ja **testaa**, että tulos on yhä oikein.
5. **Mittaa uudelleen** samalla tavalla. Jos muutos ei auttanut, peru
   se: jokainen optimointi tekee koodista vaikeamman ylläpitää.

Donald Knuthin usein lainattu lause ”ennenaikainen optimointi on kaiken
pahan alku” jatkuu harvemmin lainatulla ajatuksella: kriittiset kolme
prosenttia on silti optimoitava. Taito on löytää ne kolme prosenttia.

## Ensimmäinen esimerkki

Seuraava funktio muuttaa merkkijonon kirjaimet isoiksi. Se näyttää
lineaariselta, mutta silmukan ehto laskee merkkijonon pituuden
joka kierroksella:

```{.c tiedosto="esimerkit/01-isot.c" osa="hidas"}
```

`strlen` käy koko merkkijonon läpi, joten $n$ merkin muunnos tekee
noin $n^2/2$ lukua. Kääntäjä ei voi siirtää kutsua silmukan
ulkopuolelle, koska silmukka kirjoittaa merkkijonoon eikä kääntäjä voi
todistaa, ettei pituus muutu. Korjaus on yksi rivi:

```{.c tiedosto="esimerkit/01-isot.c" osa="nopea"}
```

Jokainen tämän tutoriaalin optimointi testataan samalla tavalla:
hidas ja nopea versio ajetaan samalle syötteelle, ja tulosten on
oltava samat.

```{.c tiedosto="esimerkit/01-isot.c" osa="testi"}
```

```{.tuloste tiedosto="esimerkit/01-isot.odotettu"}
```

Mittaus kirjoittajan koneella näyttää neliöllisen kasvun: kun $n$
kaksinkertaistuu, hidas versio hidastuu noin neljä kertaa, nopea
kaksi kertaa.

```{.tuloste tiedosto="esimerkit/tulokset/01-isot.txt"}
```

Sama virhe on löytynyt tuotantokoodista monta kertaa. Tunnetuin
tapaus on suositun verkkopelin latausruutu, joka kesti minuutteja,
koska JSON-tiedoston jäsennin kutsui `sscanf`-funktiota, joka laski
koko jäljellä olevan syötteen pituuden joka kutsulla. Luvussa 4
profiloidaan juuri tällainen ohjelma.

## Kaksi tapaa ajaa esimerkit

Ajoitusmittaus ei ole toistettava: sama ohjelma antaa eri ajan eri
koneilla ja samallakin koneella eri kerroilla. Siksi tämän paketin
esimerkit toimivat kahdessa tilassa.

- **Toiminnallinen testi** (ilman argumentteja) ajaa pienen syötteen
  ja tulostaa vain deterministisiä tuloksia: summia, tiivisteitä ja
  vertailun ”samat: kylla”. Testaaja kääntää esimerkit GCC 14:llä ja
  Clang 20:llä AddressSanitizerin ja UndefinedBehaviorSanitizerin
  kanssa ja vertaa tulosteen odotettuun. Optimoitu versio on siis aina
  testattu sanitoijilla.
- **Mittaus** (argumentti `--mittaa`) käännetään optimoinneilla
  (`-O2`) ilman sanitoijia ja ajetaan suurella syötteellä. Ajat
  tulostetaan, mutta niitä ei verrata mihinkään.

Lisäksi `esimerkit/Makefile` ajaa *deterministiset* tarkistukset:
Valgrindin Cachegrind simuloi välimuistin ja haarautumisen
ennustimen ja laskee käskyt, hudit ja väärät ennusteet. Simulaatio
antaa samat luvut joka ajolla, joten Makefile voi tarkistaa esimerkiksi,
että sarakkeittainen läpikäynti tekee vähintään neljä kertaa
enemmän välimuistihutia kuin riveittäinen.

```text
make testaa              # rakenne, esimerkit sanitoijilla, tarkistukset
make -C esimerkit mittaa # ajoitusmittaukset
make -C esimerkit tulokset   # kirjan tulosteet hakemistoon tulokset/
```

Mittausten apuvälineet ovat tiedostossa `esimerkit/mittari.h`, jota
luku 2 käy läpi.

## Kirjoittajan kone

Tekstissä näytetyt ajat on mitattu neliytimisessä virtuaalikoneessa
(Intel Xeon 2,1 GHz, L1d 48 KiB ja L2 2 MiB ydintä kohden, GCC 14.2,
Linux 6.18), jota muut prosessit kuormittivat mittausten aikana. Ne
ovat suuntaa-antavia: suhteet toistuvat yleensä, mutta tarkat luvut
eivät. Omalla koneella luvut ovat erilaisia, ja juuri siksi ne kannattaa
mitata itse. Valgrindin luvut ovat samat jokaisella koneella, jolla on
sama kääntäjä ja kirjasto.

Tutoriaali ei käytä `perf`-työkalua esimerkkiajoissa, koska Linuxin
suorituskykylaskurit eivät ole käytettävissä useimmissa konteissa ja
virtuaalikoneissa. Luku 4 näyttää komennot ja kertoo, mitä niiden
tulosteesta luetaan; omalla Linux-koneella ne toimivat sellaisinaan.
