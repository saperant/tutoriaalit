# Modulaariaritmetiikka

Modulaariaritmetiikka on jakojäännösten laskentoa: kellotaulun
aritmetiikkaa, jossa 23 + 3 on 2. Se on ohjelmoinnissa kaikkialla:
kokonaislukujen ylivuoto on laskentaa modulo $2^{64}$, hajautustaulun
lokero on hajautusarvo modulo taulun koko, tarkistusnumerot ja IBAN
perustuvat jakojäännöksiin, ja julkisen avaimen salaus on
modulaaripotenssiin korottamista suurilla luvuilla.

## Jaollisuus ja Eukleideen algoritmi

Luku $a$ **jakaa** luvun $b$, $a \mid b$, jos $b = ka$ jollakin
kokonaisluvulla $k$. Jokainen kokonaisluku $a$ voidaan jakaa luvulla
$m > 0$ yksikäsitteisesti muotoon $a = qm + r$, jossa
$0 \le r < m$; $r = a \bmod m$ on **jakojäännös**.

**Suurin yhteinen tekijä** $\operatorname{syt}(a, b)$ lasketaan
**Eukleideen algoritmilla**, joka perustuu yhtälöön
$\operatorname{syt}(a, b) = \operatorname{syt}(b, a \bmod b)$:
luku jakaa sekä $a$:n että $b$:n täsmälleen silloin, kun se jakaa sekä
$b$:n että jakojäännöksen. Jäännös pienenee joka kierroksella, joten
algoritmi päättyy, ja kierroksia on logaritminen määrä.

```{.python tiedosto="esimerkit/09-eukleides.py" osa="syt"}
```

**Laajennettu Eukleideen algoritmi** palauttaa lisäksi kertoimet $x$ ja
$y$, joille $ax + by = \operatorname{syt}(a, b)$ (**Bézout'n
identiteetti**). Kertoimet kulkevat rekursiossa ylöspäin:

```{.python tiedosto="esimerkit/09-eukleides.py" osa="laajennettu"}
```

**Pienin yhteinen jaettava** saadaan suurimmasta yhteisestä
tekijästä: $\operatorname{pyj}(a, b) = ab / \operatorname{syt}(a, b)$.
Kaksi jaksollista tapahtumaa kohtaavat pyj:n välein:

```{.python tiedosto="esimerkit/09-eukleides.py" osa="pyj"}
```

```{.tuloste tiedosto="esimerkit/09-eukleides.odotettu"}
```

## Kongruenssit ja jäännökset ohjelmassa

$a \equiv b \pmod{m}$ tarkoittaa, että $m \mid (a - b)$: luvuilla on
sama jakojäännös. Kongruenssi on ekvivalenssirelaatio (luku
*Relaatiot*), ja se säilyy yhteen-, vähennys- ja kertolaskussa: jos
$a \equiv a'$ ja $b \equiv b'$, niin $a + b \equiv a' + b'$ ja
$ab \equiv a'b'$. Siksi suuren lausekkeen jäännöksen voi laskea
ottamalla jäännöksen jokaisen välivaiheen jälkeen, eivätkä luvut kasva.

Ohjelmointikielet eroavat negatiivisten lukujen jäännöksessä. Pythonin
`%` palauttaa aina jakajan merkkisen jäännöksen, mikä vastaa
matemaattista määritelmää; C:n, Javan ja JavaScriptin `%` sekä
Pythonin `math.fmod` palauttavat jaettavan merkkisen:

```{.python tiedosto="esimerkit/09-modulo.py" osa="jaannos"}
```

## Käänteisalkiot

Luvun $a$ **käänteisalkio** modulo $m$ on $a^{-1}$, jolle
$a \cdot a^{-1} \equiv 1 \pmod{m}$. Se on olemassa täsmälleen, kun
$\operatorname{syt}(a, m) = 1$: Bézout'n identiteetti $ax + my = 1$
antaa suoraan $ax \equiv 1$. Python laskee käänteisalkion
lausekkeella `pow(a, -1, m)`:

```{.python tiedosto="esimerkit/09-modulo.py" osa="kaanteis"}
```

Tämä selittää luvun *Joukot ja funktiot* havainnon: $x \mapsto 3x \bmod 8$
on bijektio, koska 3:lla on käänteisalkio, mutta $x \mapsto 2x \bmod 8$
ei ole, koska $\operatorname{syt}(2, 8) = 2$. Jos $m$ on alkuluku,
jokaisella nollasta eroavalla luvulla on käänteisalkio, ja jäännökset
muodostavat **kunnan**, jossa voi jakaa kuten rationaaliluvuilla.

## Nopea potenssi ja Fermat'n pieni lause

Modulaaripotenssi $a^e \bmod m$ lasketaan **neliöi ja kerro**
-menetelmällä, joka käy eksponentin bitit läpi ja tekee
$O(\log e)$ kertolaskua. Jäännös otetaan joka kertolaskun jälkeen,
joten luvut pysyvät pieninä (luku *Todistaminen ja invariantit*
perustelee algoritmin invariantilla).

```{.python tiedosto="esimerkit/09-modulo.py" osa="potenssi"}
```

```{.tuloste tiedosto="esimerkit/09-modulo.odotettu"}
```

**Fermat'n pieni lause**: jos $p$ on alkuluku ja $p \nmid a$, niin
$a^{p-1} \equiv 1 \pmod{p}$. Lause antaa nopean
**alkulukutestin**: jos $2^{n-1} \not\equiv 1 \pmod{n}$, $n$ ei ole
alkuluku. Kääntäen testi voi erehtyä: Carmichaelin luvut, kuten
$561 = 3 \cdot 11 \cdot 17$, läpäisevät sen kaikilla jaottomilla
kannoilla. Käytännön testit (Miller–Rabin) korjaavat tämän ja ovat
avainten luonnin perusta.

## Tarkisteet

Tarkistusnumero havaitsee näppäilyvirheen. Sen suunnittelu on
modulaariaritmetiikkaa: virheen on muutettava jäännöstä. Suomalainen
**viitenumero** painottaa numerot oikealta luvuilla 7, 3 ja 1 ja
täydentää summan seuraavaan kymmeneen:

```{.python tiedosto="esimerkit/09-tarkisteet.py" osa="viite"}
```

**IBAN** muuntaa kirjaimet luvuiksi ($A = 10$, …, $Z = 35$) ja vaatii,
että koko luku on $\equiv 1 \pmod{97}$. Koska 97 on alkuluku ja
riittävän suuri, menetelmä havaitsee kaikki yksittäiset numerovirheet
ja lähes kaikki vierekkäisten numeroiden vaihdot:

```{.python tiedosto="esimerkit/09-tarkisteet.py" osa="iban"}
```

**Henkilötunnuksen** tarkistusmerkki on yhdeksännumeroisen luvun
jäännös modulo 31, alkuluku. Yksittäinen numerovirhe muuttaa lukua
määrällä $d \cdot 10^k$, jossa $0 < \lvert d \rvert < 10$. Koska 31 ei
jaa lukua $d$ eikä potenssia $10^k$ (31 on alkuluku eikä 2 tai 5),
jäännös muuttuu aina:

```{.python tiedosto="esimerkit/09-tarkisteet.py" osa="hetu"}
```

```{.tuloste tiedosto="esimerkit/09-tarkisteet.odotettu"}
```

## Kiinalainen jäännöslause

Jos modulit $m_1, \ldots, m_k$ ovat pareittain jaottomia, kongruenssiryhmällä
$x \equiv r_i \pmod{m_i}$ on yksikäsitteinen ratkaisu modulo
$M = m_1 \cdots m_k$. Toisin sanoen luvun $x \bmod M$ ja
jäännösjonon $(x \bmod m_1, \ldots, x \bmod m_k)$ välillä on bijektio.
Ratkaisu rakennetaan käänteisalkioilla:

```{.python tiedosto="esimerkit/09-kiinalainen.py" osa="crt"}
```

Lauseella on käytännön sovelluksia: RSA-salauksen purku lasketaan
erikseen alkulukujen $p$ ja $q$ suhteen ja yhdistetään, mikä on noin
neljä kertaa nopeampaa kuin suora laskenta. Myös suurten lukujen
aritmetiikka voidaan hajauttaa pieniin moduleihin (*residue number
system*).

```{.python tiedosto="esimerkit/09-kiinalainen.py" osa="rsa"}
```

```{.tuloste tiedosto="esimerkit/09-kiinalainen.odotettu"}
```

Esimerkin luvut ovat opetuskäyttöön. Oikea RSA vaatii yli 2000-bittiset
alkuluvut ja täytteen, eikä sitä kirjoiteta itse (taito
*Kryptografia*).

## Käytännössä

- **Tunne kielesi `%`.** Pythonin jäännös on aina ei-negatiivinen
  positiivisella jakajalla; C:n, Javan ja JavaScriptin ei. Taulukon
  indeksi `(i - 1) % n` toimii Pythonissa mutta voi olla negatiivinen
  muissa kielissä.
- **Ota jäännös välivaiheissa.** Suurten tulojen ja potenssien
  jäännös lasketaan ottamalla jäännös joka askeleella; `pow(a, e, m)`
  tekee tämän puolestasi.
- **Käytä valmiita funktioita.** `math.gcd`, `math.lcm`,
  `pow(a, -1, m)` ja `pow(a, e, m)` ovat oikein ja nopeita. Oma
  toteutus kannattaa vain oppimiseksi.
- **Valitse tarkisteeseen alkulukumoduli.** Alkuluku havaitsee
  yksittäiset virheet, ja painotettu summa havaitsee myös
  vierekkäisten merkkien vaihdot. Tarkiste ei ole tietoturvaa:
  kuka tahansa voi laskea sen.
- **Varo kokonaislukujen ylivuotoa muissa kielissä.** $a \cdot b \bmod m$
  ylivuotaa 64 bitissä, jos $m > 2^{32}$; Pythonin rajoittamattomat
  kokonaisluvut piilottavat ongelman (taito *Miten tietokone laskee*).

## Itsearviointi

- Osaat laskea suurimman yhteisen tekijän Eukleideen algoritmilla ja
  Bézout'n kertoimet laajennetulla algoritmilla.
- Osaat laskea käänteisalkion ja selittää, milloin se on olemassa.
- Osaat toteuttaa nopean modulaaripotenssin ja selittää Fermat'n
  pienen lauseen ja sen käytön alkulukutestissä.
- Osaat selittää, miten tarkisteet (viitenumero, IBAN, henkilötunnus)
  havaitsevat virheitä, ja soveltaa kiinalaista jäännöslausetta.
