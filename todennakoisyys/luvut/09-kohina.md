# Kohina ja signaali-kohinasuhde

Tämä luku soveltaa kolmen edellisen luvun tuloksia mittaustekniikkaan.
Jokaisessa mittauksessa on kohinaa: lämpöliikettä, kvantisointia,
häiriöitä. Kohinaa kuvataan satunnaismuuttujana, jonka odotusarvo on
nolla ja keskihajonta $\sigma$; keskeisen raja-arvolauseen takia se on
usein likimain normaalijakautunut. Luku laskee signaali-kohinasuhteen
ja näyttää, miten keskiarvoistus parantaa mittausta
($\sigma/\sqrt{n}$), miten kohinalähteet summautuvat (varianssien
summa ja kovarianssi) ja kuinka usein kohina aiheuttaa väärän
päätöksen (normaalijakauman häntä).

## Signaali-kohinasuhde

*Signaali-kohinasuhde* (SNR) on signaalin ja kohinan tehojen suhde.
Se ilmoitetaan yleensä desibeleinä: $\mathrm{SNR_{dB}} = 10
\log_{10}(P_s / P_n)$. Amplitudeille kerroin on 20, koska teho on
amplitudin neliö. Desibeliasteikko esitellään taidossa *Matematiikan
perusteet ohjelmallisesti*. Kohinan teho on sen varianssi $\sigma^2$.

```{.python tiedosto="esimerkit/09-kohina.py" osa="snr"}
```

```{.tuloste tiedosto="esimerkit/09-kohina.odotettu" rivit="1-1"}
```

## Keskiarvoistus

$N$ riippumattoman mittauksen keskiarvossa signaali pysyy ennallaan,
mutta kohinan keskihajonta pienenee kertoimella $\sqrt{N}$. SNR
paranee siis $10 \log_{10} N$ desibeliä: jokainen nelinkertaistus tuo
noin 6 dB.

```{.python tiedosto="esimerkit/09-kohina.py" osa="keskiarvoistus"}
```

```{.tuloste tiedosto="esimerkit/09-kohina.odotettu" rivit="2-"}
```

Parannus edellyttää, että kohina on riippumatonta mittausten välillä.
Hidas ryömintä, verkkotaajuinen häiriö ja muu korreloiva häiriö eivät
keskiarvoistu pois samalla tavalla, ja niitä varten tarvitaan
suodatusta (taito *Digitaalinen signaalinkäsittely*).

## Kohinalähteiden summautuminen

Kun riippumattomat kohinat summautuvat, niiden tehot (varianssit)
laskeutuvat yhteen: kolmen ja neljän yksikön kohinat antavat viiden
yksikön kohinan, eivät seitsemän.

```{.python tiedosto="esimerkit/09-summautuminen.py" osa="riippumattomat"}
```

Jos kohinoilla on sama lähde, ne summautuvat amplitudeina. Tällöin
kohinan voi myös kumota: differentiaalinen mittaus vähentää kahdesta
kanavasta yhteisen häiriön, ja juuri siksi esimerkiksi Ethernet ja USB
käyttävät differentiaalisia pareja.

```{.python tiedosto="esimerkit/09-summautuminen.py" osa="korreloituneet"}
```

Välimuodoissa korrelaatio mitataan kovarianssilla, ja varianssin
kaava pitää paikkansa:

```{.python tiedosto="esimerkit/09-summautuminen.py" osa="kovarianssi"}
```

```{.tuloste tiedosto="esimerkit/09-summautuminen.odotettu"}
```

## Virhe kynnysilmaisussa

Digitaalinen vastaanotin päättää jokaisesta näytteestä, lähetettiinkö
nolla vai ykkönen, vertaamalla sitä kynnykseen. Jos tasojen väli on
$d$ ja kynnys niiden puolivälissä, päätös menee väärin, kun kohina
poikkeaa yli $d/2$ väärään suuntaan. Normaalijakautuneelle kohinalle
tämän todennäköisyys on jakauman häntä, jota merkitään
**Q-funktiolla**:

$$P(\text{virhe}) = Q\!\left(\frac{d}{2\sigma}\right), \qquad
  Q(x) = P(Z > x) = \tfrac{1}{2} \operatorname{erfc}\!\big(x/\sqrt{2}\big).$$

```{.python tiedosto="esimerkit/09-ilmaisu.py" osa="q"}
```

```{.tuloste tiedosto="esimerkit/09-ilmaisu.odotettu" rivit="1-3"}
```

Häntä pienenee jyrkästi: kun kohinan keskihajonta pienenee kolmasosaan,
virheitä on lähes neljäsataa kertaa vähemmän. Tämä on bittivirhesuhteen
ja signaali-kohinasuhteen yhteyden ydin, jota taito *Digitaalinen
tiedonsiirto* käyttää modulaatioiden vertailuun.

Laskelma olettaa, että peräkkäisten näytteiden kohinat ovat
riippumattomia. Tällaista kohinaa kutsutaan **valkoiseksi**: sen
peräkkäiset näytteet eivät korreloi, ja sen teho jakautuu tasaisesti
kaikille taajuuksille. Suodatus tekee kohinasta *värillistä*:

```{.python tiedosto="esimerkit/09-ilmaisu.py" osa="valkoinen"}
```

```{.tuloste tiedosto="esimerkit/09-ilmaisu.odotettu" rivit="4-"}
```

Värillisen kohinan näytteet korreloivat, joten niiden keskiarvoistus
ei paranna tulosta kertoimella $\sqrt{N}$.

## Käytännössä

- **Laske kohinabudjetti tehoina.** Riippumattomat kohinalähteet
  summautuvat neliöjuurena; suurin lähde hallitsee, joten pienten
  lähteiden pienentäminen hyödyttää vähän.
- **Keskiarvoista vain riippumatonta kohinaa.** 6 dB:n parannus
  nelinkertaisella mittausmäärällä edellyttää riippumattomuutta;
  tarkista se mittaamalla.
- **Kumoa yhteinen häiriö.** Differentiaalinen mittaus, referenssianturi
  tai yhteismuotoinen vaimennus poistavat korreloituneen häiriön,
  jota keskiarvoistus ei poista.
- **Pidä desibelit selvinä.** Teho: kerroin 10. Amplitudi: kerroin 20.
  Sekaannus aiheuttaa kahden kertoimen virheitä.

## Itsearviointi

- Osaat laskea signaali-kohinasuhteen tehoista ja amplitudeista
  desibeleinä.
- Osaat ennustaa keskiarvoistuksen vaikutuksen kohinaan ja SNR:ään.
- Osaat laskea riippumattomien ja korreloituneiden kohinalähteiden
  summan ja selittää differentiaalisen mittauksen periaatteen.
- Osaat laskea kynnysilmaisun virhetodennäköisyyden Q-funktiolla ja
  selittää, mitä valkoinen kohina tarkoittaa.
