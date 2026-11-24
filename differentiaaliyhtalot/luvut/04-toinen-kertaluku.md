# Toisen kertaluvun yhtälöt ja värähtelijät

Newtonin toinen laki $F = ma$ on toisen kertaluvun yhtälö, koska
kiihtyvyys on paikan toinen derivaatta. Jousi-massa-vaimennin,
sarja-RLC-piiri, rakennuksen huojunta ja kaiuttimen kartio noudattavat
kaikki samaa yhtälöä

$$m\,y'' + c\,y' + k\,y = F(t),$$

missä $m$ on massa (hitaus), $c$ vaimennus ja $k$ jousivakio
(jäykkyys). Tämä luku ratkaisee yhtälön ja tulkitsee ratkaisun:
milloin järjestelmä värähtelee, kuinka nopeasti värähtely vaimenee ja
mitä tapahtuu, kun sitä pakotetaan omalla taajuudellaan.

## Homogeeninen yhtälö ja karakteristinen yhtälö

Homogeenisessa yhtälössä $F = 0$. Yrite $y = e^{\lambda t}$ muuttaa
differentiaaliyhtälön algebralliseksi **karakteristiseksi yhtälöksi**

$$m\lambda^2 + c\lambda + k = 0.$$

Juuret määräävät ratkaisun muodon:

| Juuret | Ratkaisu | Nimi |
|--------|----------|------|
| kaksi eri reaalista $\lambda_1, \lambda_2$ | $C_1 e^{\lambda_1 t} + C_2 e^{\lambda_2 t}$ | ylivaimennettu |
| kaksoisjuuri $\lambda$ | $(C_1 + C_2 t)\,e^{\lambda t}$ | kriittisesti vaimennettu |
| kompleksiset $\alpha \pm i\beta$ | $e^{\alpha t}(C_1\cos\beta t + C_2\sin\beta t)$ | alivaimennettu |

Vaimennuksen määrää yksi dimensioton luku, **vaimennussuhde**
$\zeta = c / (2\sqrt{km})$. Kun $\zeta < 1$, järjestelmä värähtelee;
kun $\zeta = 1$, se palaa lepoon nopeimmin värähtelemättä; kun
$\zeta > 1$, se palaa hitaasti.

```{.python tiedosto="esimerkit/04-vaimennus.py" osa="tapaukset"}
```

```{.tuloste tiedosto="esimerkit/04-vaimennus.odotettu"}
```

Kriittisen tapauksen kaksoisjuuri $-2$ tuottaa ratkaisuun termin
$t\,e^{-2t}$: pelkkä $e^{-2t}$ ei riittäisi kahden alkuehdon
toteuttamiseen.

![Massa poikkeutetaan yhden yksikön verran ja päästetään irti. Pieni
vaimennus jättää värähtelyn päälle, kriittinen vaimennus palauttaa
nopeimmin ilman ylitystä.](kuvat/vaimennus.png){width=76%}

Kuvasta näkee insinöörin valinnan: auton iskunvaimennin mitoitetaan
lähelle kriittistä vaimennusta (tyypillisesti $\zeta \approx 0{,}3\ldots0{,}5$
mukavuuden vuoksi), mittarin osoitin lähelle kriittistä, jotta lukema
asettuu nopeasti heilumatta.

## Pakotettu värähtely

Kun järjestelmää pakotetaan siniherätteellä $F(t) = \cos\omega t$, ratkaisu
on homogeenisen ratkaisun ja **yksityisratkaisun** summa. Homogeeninen
osa vaimenee (jos $c > 0$), joten pitkän ajan kuluttua jäljelle jää vain
yksityisratkaisu: värähtely herätteen taajuudella. Sen löytää
**määräämättömien kertoimien** menetelmällä: yritteeksi
$A\cos\omega t + B\sin\omega t$, sijoitus ja kertoimien vertailu.

```{.python tiedosto="esimerkit/04-pakotettu.py" osa="yksityis"}
```

Amplitudi on

$$\frac{1}{\sqrt{(k - m\omega^2)^2 + (c\,\omega)^2}},$$

ja se on suurimmillaan lähellä **ominaiskulmataajuutta**
$\omega_0 = \sqrt{k/m}$. Ilmiö on **resonanssi**.

```{.python tiedosto="esimerkit/04-pakotettu.py" osa="resonanssi"}
```

Resonanssihuippu on hieman ominaistaajuuden alapuolella, kohdassa
$\omega_0\sqrt{1 - 2\zeta^2}$. Simulointi vahvistaa kaavan:
jatkuvuustilan amplitudi on sama neljän desimaalin tarkkuudella.

```{.python tiedosto="esimerkit/04-pakotettu.py" osa="numeerinen"}
```

```{.tuloste tiedosto="esimerkit/04-pakotettu.odotettu"}
```

![Pakotetun värähtelyn amplitudi taajuuden funktiona eri
vaimennussuhteilla, kun $\omega_0 = 2$. Pieni vaimennus tekee
resonanssista terävän ja korkean.](kuvat/resonanssi.png){width=76%}

Resonanssi on sekä hyöty että vaara. Radiovastaanottimen värähtelypiiri
käyttää sitä valitakseen yhden taajuuden; silta, kone tai piirilevyn
komponentti voi hajota, jos herätteen taajuus osuu sen ominaistaajuuteen
ja vaimennus on pieni.

## Vaimentamaton resonanssi ja huojunta

Kun vaimennusta ei ole ja heräte osuu täsmälleen ominaistaajuuteen,
yrite $A\cos\omega t + B\sin\omega t$ ei kelpaa: se ratkaisee jo
homogeenisen yhtälön, joten sijoitus antaa nollan. Yksityisratkaisu
saadaan kertomalla yrite $t$:llä, ja amplitudi kasvaa lineaarisesti
rajatta.

```{.python tiedosto="esimerkit/04-huojunta.py" osa="resonanssi"}
```

Lähellä ominaistaajuutta amplitudi ei kasva rajatta, vaan vaihtelee
hitaasti. Kahden kosinin erotus on tulona kirjoitettuna nopea värähtely
kerrottuna hitaalla verhokäyrällä: **huojunta**. Huojunnan jakso on
$2\pi/|\omega_0 - \omega|$, joten mitä lähempänä taajuudet ovat, sitä
hitaammin amplitudi vaihtelee ja sitä suuremmaksi se ehtii kasvaa.

```{.python tiedosto="esimerkit/04-huojunta.py" osa="huojunta"}
```

```{.tuloste tiedosto="esimerkit/04-huojunta.odotettu"}
```

Soittajat virittävät kitaran kuuntelemalla huojuntaa: kahden lähes
saman sävelen yhteissoitto ”väreilee”, ja väreily hidastuu, kun
taajuudet lähestyvät toisiaan.

## Jousi-massa ja RLC: sama yhtälö

Sarja-RLC-piirin varaukselle $q$ pätee $L q'' + R q' + q/C = U(t)$, joka
on täsmälleen jousi-massa-vaimentimen yhtälö: induktanssi vastaa massaa,
resistanssi vaimennusta ja käänteiskapasitanssi jousivakiota.

| Mekaniikka | Sähkö | Rooli |
|------------|-------|-------|
| siirtymä $x$ | varaus $q$ | tilasuure |
| nopeus $x'$ | virta $i$ | muutosnopeus |
| massa $m$ | induktanssi $L$ | hitaus |
| vaimennus $c$ | resistanssi $R$ | energian häviö |
| jousivakio $k$ | $1/C$ | energian varastointi |
| voima $F$ | jännite $U$ | heräte |

```{.python tiedosto="esimerkit/04-rlc.py" osa="analogia"}
```

```{.tuloste tiedosto="esimerkit/04-rlc.odotettu"}
```

Analogia on käytännöllinen: mekaanisen järjestelmän voi simuloida
piirisimulaattorilla, ja piirin käytöksen voi ymmärtää mekaanisen
intuition avulla. Kymmenkertainen vastus muuttaa RLC-piirin
alivaimennetusta kriittisesti vaimennetuksi, kuten iskunvaimentimen
vaihto autossa.

## Samat laskut Maximalla

Maximan `ode2` ratkaisee vakiokertoimiset toisen kertaluvun yhtälöt, ja
`ic2` sijoittaa kaksi alkuehtoa. Pakotetun yhtälön yleisessä
ratkaisussa vakiot ovat `%k1` ja `%k2`.

```{.maxima tiedosto="esimerkit/maxima/04-toinen.mac" osa="toinen"}
```

```{.tuloste tiedosto="esimerkit/maxima/04-toinen.odotettu"}
```

Ilman vaimennusta pakotettu värähtelijä $y'' + 4y = \cos t$ ei koskaan
asetu: homogeeninen osa $\sin 2t$, $\cos 2t$ värähtelee ikuisesti
herätteen rinnalla.

## Käytännössä

- **Laske ensin $\omega_0$ ja $\zeta$.** Ne kertovat vasteen luonteen
  ilman ratkaisua: värähteleekö järjestelmä, millä taajuudella ja
  kuinka nopeasti se asettuu (aikavakio noin $1/(\zeta\omega_0)$).
- **Erota transientti ja jatkuvuustila.** Mittauksissa ja
  simuloinneissa jatkuvuustila näkyy vasta, kun transientti on
  vaimentunut; odota useita aikavakioita.
- **Mitoita vaimennus tarkoituksen mukaan.** Nopea asettuminen ilman
  ylitystä vaatii $\zeta \approx 0{,}7\ldots1$; resonanssin välttäminen
  vaatii, että herätteen taajuudet ovat kaukana $\omega_0$:sta.
- **Käytä analogioita.** Jousi-massa ja RLC ovat sama yhtälö; työkalut ja
  intuitio siirtyvät suoraan.

## Itsearviointi

- Osaat muodostaa karakteristisen yhtälön ja kirjoittaa homogeenisen
  ratkaisun sen juurten perusteella.
- Osaat laskea vaimennussuhteen ja ominaiskulmataajuuden ja päätellä
  niistä vasteen luonteen.
- Osaat ratkaista pakotetun värähtelyn yksityisratkaisun
  määräämättömien kertoimien menetelmällä.
- Osaat selittää resonanssin ja sen riippuvuuden vaimennuksesta.
- Osaat muuntaa mekaanisen järjestelmän sähköiseksi analogiaksi ja
  päinvastoin.
