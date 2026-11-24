# Suorituskykymittausten tulkinta

Vasteajat, läpäisyt ja käännösajat ovat satunnaismuuttujia. Niiden
jakaumat ovat vinoja ja raskashäntäisiä, joten keskiarvo kertoo niistä
vähän. Tämä luku soveltaa edellisten lukujen menetelmiä
suorituskyvyn mittaamiseen.

## Keskiarvo, mediaani ja persentiilit

Simuloidaan palvelu, joka vastaa yleensä noin 20 millisekunnissa,
mutta 2 %:ssa pyynnöistä hitaasti esimerkiksi välimuistin ohituksen tai
roskienkeruun takia:

```{.python tiedosto="esimerkit/13-mittaukset.py" osa="viiveet"}
```

Keskiarvo 29 ms ei vastaa yhtään todellista pyyntöä: tyypillinen
pyyntö on nopeampi, ja hidas pyyntö paljon hitaampi. *Mediaani* (p50)
kertoo tyypillisen kokemuksen, ja korkeat persentiilit (p99, p99,9)
kertovat hännän, jonka käyttäjät huomaavat. Palvelutasot (SLO)
määritellään siksi persentiileinä.

## Toistojen määrä

Korkean persentiilin arvio vaatii paljon havaintoja: p99:n arvioon
vaikuttaa vain yksi havainto sadasta. Toistetaan mittaus 200 kertaa
kullakin otoskoolla:

```{.python tiedosto="esimerkit/13-mittaukset.py" osa="toistot"}
```

Sadan pyynnön mittauksesta p99 voi olla mitä tahansa 36 ja 633
millisekunnin väliltä. Nyrkkisääntö: persentiilin $p$ arvioon tarvitaan
vähintään muutama kymmenen havaintoa hännästä eli noin $50/(1 - p)$
havaintoa.

## Kahden version vertailu

Onko uusi versio nopeampi? Mediaanien erotuksen bootstrap-väli vastaa
kysymykseen ilman jakaumaoletuksia:

```{.python tiedosto="esimerkit/13-mittaukset.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/13-mittaukset.odotettu"}
```

Väli ei sisällä nollaa, joten 5 %:n parannus näkyy 2000 pyynnön
mittauksesta. Erotuksen väli on parempi kuin kaksi erillistä
luottamusväliä, joiden päällekkäisyyttä katsotaan silmällä.

## Häntäviive hajautetussa järjestelmässä

Kun käyttäjän pyyntö hajautetaan sadalle palvelimelle ja vastaus
odottaa niistä hitainta, yksittäisen palvelimen harvinainen hitaus
muuttuu tavalliseksi:

```{.python tiedosto="esimerkit/13-hanta.py" osa="teoria"}
```

Simulaatio vahvistaa ilmiön: kokonaispyynnön *mediaani* on hitaampi
kuin yksittäisen palvelimen p99. *Varapyyntö* (*hedged request*)
lähettää pyynnön toiselle palvelimelle, jos vastausta ei kuulu
p95-ajassa, ja käyttää nopeampaa vastausta. Lisäkuormaa tulee vain
5 %, ja häntä lyhenee:

```{.python tiedosto="esimerkit/13-hanta.py" osa="simulointi"}
```

```{.tuloste tiedosto="esimerkit/13-hanta.odotettu"}
```

## Käytännössä

- **Raportoi persentiilit, älä keskiarvoa.** Mediaani ja p99 kertovat
  tyypillisen ja huonon kokemuksen; keskiarvo sekoittaa ne.
- **Mitoita mittaus persentiilin mukaan.** p99 vaatii tuhansia ja
  p99,9 kymmeniä tuhansia havaintoja; pienestä otoksesta korkea
  persentiili on arvaus.
- **Vertaa erotuksen välillä.** Bootstrap-väli mediaanien tai
  persentiilien erotukselle kertoo, onko muutos todellinen.
- **Lämmitä ja toista.** JIT-käännös, välimuistit ja taajuuden säätö
  tekevät ensimmäisistä mittauksista edustamattomia; hylkää ne ja
  toista mittaus eri ajoina (taito *Suorituskyky*).
- **Huomioi hajautuksen hännät.** Mitä useampaa palvelinta pyyntö
  odottaa, sitä tärkeämpi on yksittäisen palvelimen korkea
  persentiili; varapyynnöt ja aikakatkaisut leikkaavat häntää.

## Itsearviointi

- Osaat kuvata vasteaikajakauman mediaanilla ja persentiileillä ja
  selittää, miksi keskiarvo johtaa harhaan.
- Osaat arvioida, kuinka monta mittausta korkean persentiilin arvio
  tarvitsee.
- Osaat verrata kahta versiota bootstrap-välillä.
- Osaat laskea häntäviiveen vahvistumisen hajautetussa pyynnössä ja
  selittää varapyyntöjen idean.
