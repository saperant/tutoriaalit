# Analogiset modulaatiot

Amplitudimodulaatio (AM) ja taajuusmodulaatio (FM) ovat radion
vanhimmat menetelmät, ja niitä käytetään yhä yleisradiossa,
lentoradiossa ja radioamatööriliikenteessä. Ne kannattaa käydä läpi
digitaalisten modulaatioiden pohjana, koska ne esittelevät kaksi
perusajatusta: tieto voi olla kantoaallon amplitudissa tai vaiheessa,
ja vastaanotin voi joko seurata kantoaallon vaihetta (koherentti
ilmaisu) tai olla välittämättä siitä (epäkoherentti ilmaisu).

## AM ja modulaatioaste

Tavallisessa AM:ssä viesti $m(t)$, $|m| \le 1$, moduloi kantoaallon
amplitudia:

$$s(t) = \bigl(1 + \mu\,m(t)\bigr)\cos(2\pi f_c t).$$

Kantataajuudella tämä on reaalinen signaali $1 + \mu m(t)$. Kantoaalto
($1$) lähetetään mukana, jotta vastaanotin voi käyttää yksinkertaista
**verhokäyräilmaisinta**: diodi tasasuuntaa signaalin, ja RC-suodin
tasoittaa kantoaallon pois. Toinen vaihtoehto on **koherentti ilmaisu**,
jossa signaali kerrotaan paikallisella kantoaallolla kuten luvussa 2.

```{.python tiedosto="esimerkit/03-am.py" osa="ilmaisimet"}
```

Modulaatioaste $\mu$ ratkaisee, toimiiko verhokäyräilmaisin. Kun
$\mu > 1$, verhokäyrä $1 + \mu m$ menee välillä negatiiviseksi, ja
tasasuuntaus kääntää sen: ilmaistu viesti vääristyy. Koherentti
ilmaisin ei välitä tästä, koska se säilyttää etumerkin.

```{.python tiedosto="esimerkit/03-am.py" osa="aste"}
```

Kolmas sarake kertoo AM:n heikkouden: suurin osa lähetystehosta kuluu
kantoaaltoon, joka ei kuljeta tietoa. Täydelläkin modulaatiolla
viestin osuus jää tässä 22 prosenttiin.

**DSB-SC** (*double sideband, suppressed carrier*) jättää kantoaallon
pois, jolloin koko teho on viestissä. Hinta on se, että vastaanottimen
on tiedettävä kantoaallon vaihe. Vaihevirhe $\varphi$ kertoo
ilmaistun signaalin tekijällä $\cos\varphi$:

```{.python tiedosto="esimerkit/03-am.py" osa="vaihe"}
```

```{.tuloste tiedosto="esimerkit/03-am.odotettu"}
```

Kun vaihe on 90 astetta väärin, signaali katoaa kokonaan. Tämä on
digitaalisen tiedonsiirron synkronointiongelman alkumuoto: koherentti
ilmaisu on tehokkaampi, mutta se vaatii kantoaallon palauttamista
(luku 7). **SSB** (*single sideband*) poistaa lisäksi toisen
sivukaistan ja puolittaa kaistan. Se on kantataajuudella kompleksinen
signaali $m(t) + i\,\hat m(t)$, jossa $\hat m$ on viestin
Hilbert-muunnos.

## FM: modulaatioindeksi ja kaista

Taajuusmodulaatiossa viesti ohjaa hetkellistä taajuutta:
$f(t) = f_c + \Delta f\,m(t)$. Vaihe on taajuuden integraali, joten
kantataajuussignaali on

$$x(t) = \exp\Bigl(i\,2\pi\Delta f\int_0^t m(\tau)\,d\tau\Bigr).$$

Signaalin amplitudi on vakio, mikä tekee FM:stä epäherkän
amplitudikohinalle ja sallii epälineaariset, hyötysuhteeltaan hyvät
tehovahvistimet.

```{.python tiedosto="esimerkit/03-fm.py" osa="moduloi"}
```

Sinimuotoisella viestillä spektri koostuu viivoista taajuuksilla
$f_c + k f_m$, ja niiden amplitudit ovat Besselin funktioita
$J_k(\beta)$, missä **modulaatioindeksi** on $\beta = \Delta f / f_m$:

```{.python tiedosto="esimerkit/03-fm.py" osa="besselit"}
```

Spektri on teoriassa ääretön, mutta lähes kaikki teho on
**Carsonin säännön** kaistan sisällä:

$$B \approx 2(\Delta f + f_m).$$

```{.python tiedosto="esimerkit/03-fm.py" osa="kaista"}
```

## FM:n ilmaisu vaihe-erolla

Kantataajuudella hetkellinen taajuus on vaiheen derivaatta. Näytteistä
se lasketaan peräkkäisten näytteiden vaihe-erona: $z[n]\,z^*[n-1]$ on
kompleksiluku, jonka kulma on vaiheen muutos näytevälissä. Menetelmä
ei välitä signaalin amplitudista eikä alkuvaiheesta, joten sitä
käytetään myös digitaalisen FSK:n ilmaisussa ja taajuusvirheen
estimoinnissa (luku 7).

```{.python tiedosto="esimerkit/03-fm.py" osa="demoduloi"}
```

```{.tuloste tiedosto="esimerkit/03-fm.odotettu"}
```

Mitatut viivat osuvat Besselin funktioihin neljän desimaalin
tarkkuudella. Carsonin kaista 12 kHz sisältää 99,4 % tehosta, kun pelkkä
kaksinkertainen poikkeama 10 kHz jättää ulkopuolelle 4 %. Demoduloitu
viesti palautuu kohinasta huolimatta, ja vastaanotetun signaalin
amplitudi (tässä 0,3) ei vaikuta tulokseen.

## Käytännössä

- **AM:n etu on yksinkertainen vastaanotin, haitta teho.**
  Verhokäyräilmaisin on diodi ja kondensaattori, mutta kantoaalto
  kuluttaa yli kaksi kolmasosaa tehosta. Siksi AM on jäänyt
  käyttökohteisiin, joissa vastaanottimen hinta tai yksinkertaisuus on
  tärkeintä.
- **Koherentti ilmaisu tarvitsee vaiheen.** Vaihevirhe vaimentaa
  signaalia tekijällä $\cos\varphi$ ja pyörittää kompleksisessa
  tapauksessa signaalia I- ja Q-haarojen välillä. Sama ongelma
  toistuu kaikissa digitaalisissa modulaatioissa.
- **Mitoita FM:n kaista Carsonin säännöllä** ja tarkista simuloimalla.
  FM vaihtaa kaistaa signaali-kohinasuhteeseen: suuri
  modulaatioindeksi kuluttaa kaistaa mutta parantaa ilmaistun viestin
  laatua, kunnes signaali on kohinakynnyksen alla.
- **Vaihe-eroilmaisin on monikäyttöinen.** $\arg(z[n]\,z^*[n-1])$
  antaa hetkellisen taajuuden ilman kantoaallon palautusta. Se
  ilmaisee FM:n ja FSK:n ja estimoi taajuusvirheen.

## Itsearviointi

- Osaat simuloida AM-modulaation ja selittää, miksi verhokäyräilmaisin
  vaatii modulaatioasteen $\mu \le 1$.
- Osaat laskea, kuinka suuri osa AM-signaalin tehosta on viestissä,
  ja selittää DSB-SC:n ja SSB:n edut ja hinnan.
- Osaat selittää, miten kantoaallon vaihevirhe vaikuttaa koherenttiin
  ilmaisuun.
- Osaat laskea FM-signaalin modulaatioindeksin ja Carsonin kaistan sekä
  ilmaista FM:n vaihe-erolla.
