# Kääntäjän testaus

Kääntäjän virhe on poikkeuksellisen vahingollinen. Se ei näy
kääntäjässä vaan käännetyssä ohjelmassa, joka laskee väärin harvoin ja
vain tietyillä syötteillä, ja ohjelmoija etsii virhettä ensin
omasta koodistaan. Siksi kääntäjiä testataan monella tasolla. Tämä luku
käy läpi Kiden testisarjan, jonka `make` ajaa ja joka kulkee myös
jatkuvassa integraatiossa.

## Kääntäjä sanitoijien kanssa

Kääntäjä itse käännetään kahdella kääntäjällä, varoitukset virheinä ja
AddressSanitizerin ja UndefinedBehaviorSanitizerin kanssa:

```{.make tiedosto="esimerkit/Makefile" osa="liput"}
```

Kaksi kääntäjää löytävät eri varoituksia, ja sanitoijat pysäyttävät
kääntäjän muistivirheeseen tai määrittelemättömään käytökseen heti
virheen kohdalla eikä vasta, kun väärä arvo päätyy tulosteeseen.
Esimerkiksi laskostuksessa etumerkillinen ylivuoto olisi
UBSan-virhe; koska aritmetiikka on toteutettu etumerkittömänä (luku 2),
sitä ei synny.

## Kultaiset tulosteet

Testiohjelmat ovat hakemistossa `ohjelmat/`, ja jokaisella on
odotettu tuloste. Ohjelmat on valittu niin, että ne harjoittavat
kääntäjän eri osia:

| Ohjelma | Mitä se testaa |
|---------|----------------|
| `kertoma`, `fibonacci` | rekursio, silmukat, kutsut |
| `syt`, `potenssi` | jakolasku ja jäännös, parametrien muuttaminen |
| `alkuluvut`, `oikosulku` | oikosulku ja sivuvaikutukset |
| `collatz` | sisäkkäiset ehdot, pitkät silmukat |
| `semantiikka` | ylivuoto, nollalla jakaminen, laskostus |
| `nakyvyys` | näkyvyysalueet ja peittäminen |
| `parametrit` | kahdeksan argumenttia rekistereissä |
| `paine` | 12 yhtä aikaa elävää arvoa, pinoon vienti |

Jokainen ohjelma ajetaan tulkilla molemmilla kääntäjillä ja käännettynä
kuudella valintayhdistelmällä sekä Clangilla käännetyllä kääntäjällä:

```{.bash tiedosto="esimerkit/testaa.sh" osa="valinnat"}
```

Valinnat on valittu niin, että jokainen takaosan polku tulee
suoritetuksi: ilman optimointeja ja niiden kanssa, kaikki pinoon ja
lineaarinen varaus, sekä varaus yhdellä ja kahdella rekisterillä, jolloin
pinoon vienti on jatkuvaa. Tavallisella rekisterimäärällä
`paine`-ohjelma on ainoa, joka vie arvoja pinoon.

Virheohjelmilla (luvut 3, 6 ja 7) on odotettu virhetuloste, ja
tekstissä näytetyt välitulosteet (`naytteet/`) ovat myös kultaisia
tiedostoja: jos jäsennin tai optimointi muuttuu, tutoriaalin tekstin
tulosteet eivät voi jäädä vanhoiksi. Kultaisten tulosteiden heikkous on
ylläpito: kun tuloste muuttuu tarkoituksella, `make naytteet` kirjoittaa
ne uudelleen, ja muutos tarkistetaan versionhallinnan erotuksesta.

## Differentiaalitestaus

Käsin kirjoitettuja testiohjelmia on kymmenkunta. Kääntäjän virheet
piileskelevät kuitenkin harvinaisissa yhdistelmissä: vakio
vertailun oikealla puolella, `%` negatiivisella luvulla, kopio
silmukan paluukaarella. **Differentiaalitestaus** generoi satunnaisia
ohjelmia ja vertaa kahden toteutuksen tuloksia. Oikeaa vastausta ei
tarvitse tietää: riittää, että tulkki ja käännetty ohjelma ovat samaa
mieltä.

Generaattorin on tuotettava ohjelmia, jotka ovat *oikeellisia* ja
*päättyviä* ja joiden tulos on *määritelty*. Kide tekee viimeisestä
helppoa, koska kaikki aritmetiikka on määriteltyä (luku 2). C:lle
vastaava generaattori Csmith joutuu välttämään jokaisen määrittelemättömän
käytöksen, ja se on sen monimutkaisin osa. Lausekkeiden generointi:

```{.python tiedosto="esimerkit/satunnainen.py" osa="lausekkeet"}
```

Päättyminen taataan rakenteella: funktio kutsuu vain aiemmin
määriteltyjä funktioita (ei rekursiota), ja silmukat ovat
laskurisilmukoita, joiden laskuria runko ei saa muuttaa. Siemen tekee
generoinnista toistettavan, joten jokainen löydetty virhe on
toistettavissa siemenen numerolla. Testiajuri:

```{.bash tiedosto="esimerkit/testaa.sh" osa="satunnaiset"}
```

Kun tätä tutoriaalia kirjoitettiin, 200 satunnaisohjelmaa ajettiin
kolmella valintayhdistelmällä ennen kuin testisarja rajattiin 40:een
(ajoaika). Csmith löysi vuosina 2008–2011 GCC:stä ja LLVM:stä yli 325
virhettä samalla periaatteella (Yang ym. 2011), ja nykyään
tuotantokääntäjiä sumeutetaan jatkuvasti.

## Testien teho

Mistä tietää, että testit löytävät virheitä? Testisarja kääntää
kääntäjästä myös tarkoituksella rikotun version, jossa `<=` käännetään
kuten `<` (makro `KIDE_VIKA` koodingeneraattorissa). Vika näkyy vain,
kun vertailun operandit ovat yhtä suuret, joten se on realistinen
"melkein oikein" -virhe. Testiajuri vaatii, että satunnaisohjelmat
paljastavat sen, ja raportoi tuloksen:
*Vika löytyi 1/40 ohjelmasta (ensimmäinen: siemen 9).*

Tulos on opettavainen. Satunnaisohjelmista vain yksi neljästäkymmenestä
paljastaa vian, koska satunnaisilla luvuilla yhtäsuuruus on harvinaista.
Käsin kirjoitetut ohjelmat (`kertoma` vertaa `n <= 1` ja silmukat
`i <= 10`) paljastavat sen jokaisella ajolla. Testityypit täydentävät
toisiaan: kultaiset testit kattavat tunnetut reunatapaukset,
satunnaistestit tuntemattomat yhdistelmät. Tätä menetelmää, jossa
ohjelmaan istutetaan vikoja ja mitataan, kuinka moni löytyy, kutsutaan
**mutaatiotestaukseksi**; taito *Laitteiston verifiointi* käyttää
samaa ajatusta.

## Virheen pienentäminen

Satunnaisohjelma, joka paljastaa virheen, on usein satoja rivejä pitkä.
Ennen virheen etsimistä se **pienennetään** (*test case reduction*):
poistetaan lauseita ja yksinkertaistetaan lausekkeita yksi kerrallaan
niin kauan kuin virhe säilyy. Työkalut kuten C-Reduce (muillekin kielille valinnalla `--not-c`)
ja Perses tekevät tämän automaattisesti delta-debuggauksen
(Zeller ja Hildebrandt 2002) periaatteella. Pienennetty ohjelma lisätään kultaisiin testeihin, jotta
virhe ei palaa.

## Käytännössä

- **Käännä kääntäjä sanitoijien kanssa testejä varten.** Kääntäjän oma
  muistivirhe näkyy muuten satunnaisena vääränä koodina.
- **Tulkki on paras oraakkeli.** Viitetoteutus tekee
  differentiaalitestauksesta mahdollista ilman odotettuja tuloksia.
  Toinen kääntäjä (tai sama kääntäjä eri optimointitasolla) on toinen
  hyvä oraakkeli.
- **Generoi vain määriteltyjä ohjelmia.** Muuten erot johtuvat
  ohjelmasta eivätkä kääntäjästä.
- **Mittaa testien teho.** Istutettu vika, jota testit eivät löydä,
  kertoo aukon testisarjassa.
- **Testaa jokainen takaosan polku.** Rekisteripula, suuret siirtymät ja
  harvinaiset käskymuodot suoritetaan vain, jos testit pakottavat ne.

## Itsearviointi

- Osaat suunnitella kääntäjälle testisarjan, jossa on kultaisia
  tulosteita, virheohjelmia ja välitulosteiden näytteitä.
- Osaat kirjoittaa satunnaisohjelmien generaattorin, jonka ohjelmat
  ovat oikeellisia, päättyviä ja määriteltyjä.
- Osaat käyttää tulkkia oraakkelina differentiaalitestauksessa ja
  toistaa virheen siemenellä.
- Osaat arvioida testisarjan tehoa istutetulla vialla ja selittää,
  miksi käsin kirjoitetut ja satunnaiset testit täydentävät toisiaan.
