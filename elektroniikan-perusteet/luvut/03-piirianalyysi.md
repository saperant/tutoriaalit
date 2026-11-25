# Piirianalyysi

Yksinkertaisen piirin voi ratkaista sarja- ja rinnankytkentöjä
yhdistelemällä, mutta kun piirissä on useita lähteitä tai silmukoita,
tarvitaan järjestelmällinen menetelmä. Tässä luvussa käydään läpi
Kirchhoffin lait, solmujännitemenetelmä matriisimuodossa sekä
Theveninin vastine ja superpositio. Samat menetelmät ovat SPICEn
sisällä: simulaattori kokoaa piiristä yhtälöryhmän ja ratkaisee sen.

## Kirchhoffin lait

**Virtalaki** (KCL): solmuun tulevien virtojen summa on yhtä suuri kuin
solmusta lähtevien virtojen summa. Varaus ei katoa eikä kasaannu
johtimeen.

**Jännitelaki** (KVL): minkä tahansa suljetun silmukan jännitteiden
summa on nolla. Kun kierretään silmukka ja palataan lähtöpisteeseen,
potentiaali on sama kuin lähtiessä.

Näistä seuraavat tutut säännöt:

| Kytkentä | Kokonaisresistanssi | Mikä on yhteistä |
|----------|---------------------|------------------|
| sarjaan | $R = R_1 + R_2 + \dots$ | virta |
| rinnan | $1/R = 1/R_1 + 1/R_2 + \dots$ | jännite |

Rinnankytkentä on helpointa laskea konduktansseilla $G = 1/R$
(yksikkö siemens, S), jotka summautuvat suoraan. Kahden vastuksen
rinnankytkentä on $R_1 R_2 / (R_1 + R_2)$.

## Solmujännitemenetelmä

Solmujännitemenetelmä on järjestelmällinen tapa ratkaista mikä
tahansa vastuksista ja lähteistä koostuva piiri:

1. Valitaan maasolmu (jännite 0).
2. Muille solmuille annetaan tuntemattomat jännitteet.
3. Jokaiseen tuntemattomaan solmuun kirjoitetaan virtalaki:
   solmusta lähtevien virtojen summa on nolla. Vastuksen läpi lähtevä
   virta on $(U_\text{tämä} - U_\text{naapuri}) / R$.
4. Ratkaistaan lineaarinen yhtälöryhmä.

![Kahden lähteen silta. Tuntemattomat ovat solmujännitteet a ja
b.](kuvat/silta.png){width=62%}

Kuvan piirissä on kaksi tuntematonta solmua. Kun virtalait kirjoitetaan
konduktansseilla ja tuntemattomat kootaan vasemmalle, saadaan
matriisiyhtälö $G\,u = i$, jonka NumPy ratkaisee:

```{.python tiedosto="esimerkit/03-solmut.py" osa="matriisi"}
```

Matriisin rakenne on säännöllinen: diagonaalilla on kuhunkin solmuun
liittyvien konduktanssien summa, ja diagonaalin ulkopuolella on
solmujen välisen konduktanssin vastaluku. Oikean puolen vektori
sisältää lähteistä tulevat virrat. Tämä *konduktanssimatriisi* on
juuri se, minkä SPICE kokoaa netlististä (lähteet se käsittelee
laajennetulla menetelmällä, *modified nodal analysis*, jossa
jännitelähteiden virrat ovat lisätuntemattomia).

```{.spice tiedosto="esimerkit/03-solmut.cir"}
```

```{.tuloste tiedosto="esimerkit/03-solmut.odotettu"}
```

Silmukkavirtamenetelmä on solmujännitemenetelmän pari: tuntemattomina
ovat silmukoiden virrat ja yhtälöinä jännitelait. Se on kätevä, kun
piirissä on vähän silmukoita ja paljon solmuja, mutta solmumenetelmä
on yleisempi ja helpompi automatisoida, ja siksi simulaattorit
käyttävät sitä.

## Symbolinen ratkaisu SymPyllä

Numeerinen ratkaisu kertoo, mitä yksi piiri tekee. Symbolinen ratkaisu
kertoo, miten tulos riippuu komponenteista, ja siitä näkee
mitoitussäännön. SymPy ratkaisee kuormitetun jakajan solmuyhtälön
kirjainsymboleilla (työkalun perusteet ovat taidon *Matematiikan
perusteet ohjelmallisesti* luvussa 2):

```{.python tiedosto="esimerkit/03-symbolinen.py" osa="symbolinen"}
```

```{.python tiedosto="esimerkit/03-symbolinen.py" osa="numero"}
```

```{.tuloste tiedosto="esimerkit/03-symbolinen.odotettu"}
```

Raja-arvo $R_L \to \infty$ antaa kuormittamattoman jakajan kaavan, ja
kaavan nimittäjästä näkee, että kuorma vaikuttaa vähän vain, kun
$R_L \gg R_1 R_2 / (R_1 + R_2)$. Tämä lauseke on jakajan
lähtöresistanssi, joka tulee vastaan seuraavassa osiossa. 10 kΩ:n
kuorma pudottaa jakajan 3,84 V:n lähdön 2,91 V:iin.

## Theveninin ja Nortonin vastineet

Mikä tahansa lineaarinen piiri näyttää kahden navan välistä katsottuna
samalta kuin jännitelähde $U_\text{th}$ sarjassa vastuksen
$R_\text{th}$ kanssa (**Theveninin vastine**) tai virtalähde
$I_N = U_\text{th} / R_\text{th}$ rinnan saman vastuksen kanssa
(**Nortonin vastine**). Vastine tiivistää monimutkaisen piirin kahteen
lukuun, ja sillä on helppo laskea, mitä tapahtuu, kun napoihin
kytketään kuorma.

- $U_\text{th}$ on napojen jännite ilman kuormaa (tyhjäkäyntijännite).
- $R_\text{th}$ on napojen välinen resistanssi, kun jännitelähteet
  oikosuljetaan ja virtalähteet avataan. Se on piirin
  *lähtöimpedanssi*.

Vastineen voi myös mitata. Kun napoista otetaan kasvava kuormavirta,
jännite laskee suoraviivaisesti: $U = U_\text{th} - R_\text{th} I$.
Suoran leikkauspiste on $U_\text{th}$ ja kulmakerroin $-R_\text{th}$.
Sama menetelmä toimii laboratoriossa oikealle piirille.

```{.spice tiedosto="esimerkit/03-thevenin.cir"}
```

`dc Ikuorma 0 2m 0.1m` pyyhkäisee virtalähteen arvoa, ja `wrdata`
kirjoittaa tulokset tiedostoon. Python sovittaa suoran pienimmän
neliösumman menetelmällä ja vertaa tulosta käsin laskettuun:

```{.python tiedosto="esimerkit/03-thevenin.py" osa="kasin"}
```

```{.python tiedosto="esimerkit/03-thevenin.py" osa="sovitus"}
```

```{.tuloste tiedosto="esimerkit/03-thevenin.odotettu"}
```

Theveninin vastine selittää luvun 2 mittausvirheen: mittari on kuorma
piirin vastineen napoihin, ja virhe riippuu suhteesta
$R_\text{th} / R_\text{mittari}$.

Vastineesta näkee myös, mihin kuorma kannattaa mitoittaa, ja vastaus
riippuu tavoitteesta. *Jännite* siirtyy kuormaan lähes kokonaan, kun
$R_L \gg R_\text{th}$; näin kytketään signaalit, anturit ja mittarit.
*Teho* on suurimmillaan, kun $R_L = R_\text{th}$: silloin kuorma saa
tehon $U_\text{th}^2 / (4 R_\text{th})$, mutta yhtä paljon hukkuu
lähteen sisäresistanssiin, eli hyötysuhde on vain 50 %. Tehon
sovitusta käytetään siellä, missä jokainen milliwatti on saatava
talteen (antennit, radiotaajuuspiirit); teholähteissä ja vahvistimien
lähdöissä sisäresistanssi tehdään päinvastoin mahdollisimman pieneksi.

## Superpositio

Lineaarisessa piirissä (vastukset, kondensaattorit, kelat ja
riippumattomat lähteet) jokaisen lähteen vaikutuksen voi laskea
erikseen ja laskea yhteen. Muut jännitelähteet korvataan
oikosuluilla ja virtalähteet avoimilla piireillä. Python muokkaa
netlistiä tekstinä ja simuloi kolme tapausta:

```{.python tiedosto="esimerkit/03-superpositio.py" osa="superpositio"}
```

```{.tuloste tiedosto="esimerkit/03-superpositio.odotettu"}
```

Jälkimmäinen tarkistus on lineaarisuuden määritelmä: kaksinkertainen
herätys antaa kaksinkertaisen vasteen. Diodit ja transistorit ovat
epälineaarisia, eikä superpositio päde niille; niitä tarkastellaan
luvuissa 6 ja 7. Superpositio kuitenkin pätee *pienille muutoksille*
toimintapisteen ympärillä, ja sitä käytetään vahvistimien
piensignaalianalyysissä (jatkotaito *Analogiaelektroniikka*).

## Käytännössä

- Piirrä piiri ja nimeä solmut ennen laskemista. Sama nimeäminen
  kannattaa käyttää netlistissä, jolloin tulokset on helppo verrata.
- Jakaja on tarkka vain kevyesti kuormitettuna. Nyrkkisääntö:
  jakajan läpi kulkevan virran on oltava vähintään kymmenkertainen
  kuormavirtaan nähden, tai kuorma pitää laskea mukaan.
- Theveninin vastine on paras tapa ajatella liitäntöjä: anturin
  lähtöimpedanssi ja AD-muuntimen tuloimpedanssi muodostavat jakajan,
  joka joko vääristää mittausta tai ei.
- SPICE on käytännössä solmujännitemenetelmän ratkaisin. Kun simulaatio
  ei käynnisty, syy on usein solmu, jolla ei ole tasavirtareittiä
  maahan (esimerkiksi pelkän kondensaattorin takana oleva solmu), jolloin
  matriisi on singulaarinen.
- Käsinlasku ei ole turha, vaikka simulaattori on olemassa. Se kertoo,
  mitä tulosta odottaa, ja simulaattorin virheellinen netlist näkyy
  heti erona.

## Itsearviointi

- Osaat soveltaa Kirchhoffin virta- ja jännitelakia ja laskea sarja- ja
  rinnankytkennät.
- Osaat kirjoittaa piirin solmujänniteyhtälöt matriisimuotoon ja
  ratkaista ne NumPylla.
- Osaat määrittää Theveninin ja Nortonin vastineen laskemalla ja
  kuormituskäyrästä sovittamalla.
- Osaat käyttää superpositiota ja kertoa, milloin se ei päde.
- Osaat pyyhkäistä lähteen arvoa ngspicen DC-analyysillä ja käsitellä
  tuloksia Pythonilla.
