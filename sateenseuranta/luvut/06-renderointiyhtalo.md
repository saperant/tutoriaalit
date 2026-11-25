# Radiometria ja renderöintiyhtälö

Whittedin rajat johtuivat siitä, että valoa seurattiin vain muutamaan
suuntaan. Oikeasti pinta vastaanottaa valoa koko pallonpuoliskolta ja
heijastaa sitä koko pallonpuoliskolle. Jotta tämä voidaan kirjoittaa
yhtälöksi, tarvitaan suureet, jotka kertovat, kuinka paljon valoa
kulkee mihinkin suuntaan. Radiometria on fysiikan osa, joka
määrittelee ne.

## Avaruuskulma

Tason kulma on kaaren pituus yksikköympyrällä; avaruuskulma on pinta-ala
yksikköpallolla. Koko pallon avaruuskulma on $4\pi$ steradiaania,
pallonpuoliskon $2\pi$. Pallokoordinaateissa, kun $\theta$ on kulma
normaalista ja $\phi$ kiertokulma, pieni avaruuskulma on
$d\omega = \sin\theta\,d\theta\,d\phi$. Kaukaisen pienen pinnan
avaruuskulma on sen pinta-ala kerrottuna kallistuksen kosinilla ja
jaettuna etäisyyden neliöllä: $d\omega = \cos\theta'\,dA / r^2$.
Tämä muunnos pinta-alan ja avaruuskulman välillä on polunseurannan
suoran valaistuksen perusta.

## Suureet

| Suure | Merkintä | Yksikkö | Merkitys |
|-----------------|-------|----------|-------------------------------------|
| säteilyteho (vuo) | $\Phi$ | W | valon kokonaisteho |
| irradianssi | $E$ | W/m² | pinnalle tuleva teho pinta-alaa kohden |
| intensiteetti | $I$ | W/sr | pistelähteen teho avaruuskulmaa kohden |
| radianssi | $L$ | W/(m² sr) | teho pinta-alaa ja avaruuskulmaa kohden |

Radianssi on keskeinen, koska se pysyy vakiona tyhjässä tilassa säteen
suuntaan: pinnan kirkkaus ei riipu siitä, kuinka kaukaa sitä
katsotaan. Kauempana pinta näyttää pienemmältä, mutta jokaisen
näkyvän pisteen kirkkaus on sama. Kameran pikseli mittaa radianssia,
ja säteenseuranta laskee radianssia säteitä pitkin.

Irradianssi saadaan radianssista integroimalla tulevan valon yli
painotettuna kosinilla, koska vinosti tuleva valo jakautuu suuremmalle
alalle:

$$E = \int_{\Omega} L_i(\omega)\cos\theta\,d\omega.$$

Kun $L_i$ on vakio, $E = \pi L_i$: kosinin integraali pallonpuoliskon
yli on $\pi$, ei $2\pi$.

## BRDF

Pinnan heijastusta kuvaa kaksisuuntainen heijastusjakaumafunktio
BRDF (*bidirectional reflectance distribution function*)
$f(\omega_i, \omega_o)$: suuntaan $\omega_o$ heijastuvan radianssin
suhde suunnasta $\omega_i$ tulevaan irradianssiin.

![BRDF:n suureet pinnan pisteessä. Suunnasta $\omega_i$ pienestä
avaruuskulmasta $d\omega_i$ tuleva radianssi $L_i$ tuottaa
irradianssin $L_i \cos\theta_i\,d\omega_i$, ja BRDF kertoo, kuinka
suuri osa siitä lähtee suuntaan
$\omega_o$.](kuvat/06-puolipallo.png){width=58%}

Fysikaalisesti järkevällä BRDF:llä on kolme ominaisuutta:

1. **Ei-negatiivisuus**: $f \ge 0$.
2. **Vastavuoroisuus** (Helmholtz): $f(\omega_i, \omega_o) =
   f(\omega_o, \omega_i)$. Valon kulun voi kääntää, minkä ansiosta
   säteitä voi seurata kamerasta valoon päin.
3. **Energian säilyminen**: suunta-albedo
   $\int_\Omega f(\omega_i, \omega_o)\cos\theta_i\,d\omega_i \le 1$
   kaikilla $\omega_o$. Pinta ei heijasta enempää kuin siihen tulee.

Lambertin pinnan BRDF on vakio $\rho/\pi$, missä $\rho \le 1$ on
heijastuskyky (albedo). Jakaja $\pi$ tulee kosinin integraalista:
silloin albedo on täsmälleen $\rho$. Renderöinnin perusteiden
Phong-malli $k_s\cos^n\alpha$ ei säilytä energiaa ilman
normalisointia: pienellä eksponentilla se heijastaa enemmän valoa kuin
pintaan tulee, suurella paljon vähemmän. Normalisointikerroin
$(n + 2)/(2\pi)$ korjaa molemmat.

Integraalit voi tarkistaa numeerisesti. Pyörähdyssymmetrinen
integraali pallonpuoliskon yli on yksiulotteinen, ja keskipistesääntö
riittää:

```{.cpp tiedosto="esimerkit/06-radiometria.cpp" osa="puolipallo"}
```

```{.cpp tiedosto="esimerkit/06-radiometria.cpp" osa="integraalit"}
```

Normalisoimaton Phong-lohko heijastaa eksponentilla 1 kaksinkertaisesti
tulevan valon ja eksponentilla 100 vain 6 % siitä: materiaali, jonka
kiiltoa terävöitetään, himmenee.
Normalisoitu lohko heijastaa aina saman määrän. Eksponentilla 1000
keskipistesääntö alkaa jäädä jälkeen (1,00003), koska terävä lohko
tarvitsee tiheämmän jaon. Sama ilmiö palaa Monte Carlossa: terävä
integrandi tarvitsee näytteet oikeisiin kohtiin.

## Pintavalo ja käänteisen neliön laki

Pistevalon irradianssi on $I\cos\theta / r^2$. Pintavalon irradianssi
saadaan integroimalla valon pinnan yli, kun avaruuskulma muunnetaan
pinta-alaksi:

$$E = \int_A L\,\frac{\cos\theta\,\cos\theta'}{r^2}\,dA,$$

missä $\theta$ on kulma pinnan normaalista ja $\theta'$ valon
normaalista. Esimerkki laskee neliön muotoisen valon irradianssin
suoraan sen alla ja vertaa sitä pistevalon kaavaan:

```{.cpp tiedosto="esimerkit/06-radiometria.cpp" osa="pintavalo"}
```

```{.tuloste tiedosto="esimerkit/06-radiometria.odotettu"}
```

Kun etäisyys on viisi kertaa valon koko, pistevalo on alle 2 %:n
päässä. Lähellä valoa ero on suuri: kosinitermit pienenevät valon
reunoilla ja etäisyys kasvaa. Tästä seuraa käytännön nyrkkisääntö
valaistuksen suunnitteluun, ja polunseurannalle tärkeä havainto:
pintavalon integraali on hyvin käyttäytyvä, kun valo on kaukana,
mutta $1/r^2$ kasvaa rajatta valon lähellä.

## Renderöintiyhtälö

Pisteestä $\mathbf{x}$ suuntaan $\omega_o$ lähtevä radianssi on pinnan
oma säteily plus kaikista suunnista tulevan valon heijastus:

$$L_o(\mathbf{x}, \omega_o) = L_e(\mathbf{x}, \omega_o) +
\int_\Omega f(\mathbf{x}, \omega_i, \omega_o)\,
L_i(\mathbf{x}, \omega_i)\,\cos\theta_i\,d\omega_i.$$

Yhtälö on Kajiyan (1986) muotoa ja koko polunseurannan perusta. Se on
rekursiivinen: tuleva radianssi $L_i(\mathbf{x}, \omega_i)$ on
lähtevää radianssia $L_o$ pisteestä, johon säde
$\mathbf{x} + t\omega_i$ ensimmäisenä osuu. Kun sijoitetaan
yhtälö itseensä, saadaan summa

$$L = L_e + T L_e + T^2 L_e + \dots,$$

missä $T$ on yhden heijastuksen operaattori. Termi $T^k L_e$ on valo,
joka on heijastunut täsmälleen $k$ kertaa: $L_e$ näkyy suoraan, $T L_e$
on suora valaistus, $T^2 L_e$ yksi epäsuora heijastus ja niin edelleen.
Sarja suppenee, koska energian säilyminen tekee $T$:stä
supistavan: jokainen heijastus menettää osan valosta.

Tämän muodon kautta Whitted ja polunseuranta ovat saman yhtälön
approksimaatioita. Whitted laskee $T$:n vain peilisuuntiin ja
pistevaloon, ja korvaa loput vakiolla. Polunseuranta arvioi jokaisen
integraalin satunnaisella näytteellä, ja koska jokainen termi on
odotusarvoltaan oikein, myös summa on.

Integraali on moniulotteinen: $k$:n heijastuksen termi on
$2k$-ulotteinen integraali suuntien yli, ja pikselin alue,
linssin aukko, valotusaika ja aallonpituus lisäävät ulottuvuuksia.
Numeeriset kvadratuurisäännöt kuten edellä käytetty keskipistesääntö
vaativat $N^d$ pistettä $d$ ulottuvuudessa, mikä on mahdotonta jo
muutamalla heijastuksella. Monte Carlo -integroinnin virhe ei riipu
ulottuvuudesta. Siksi seuraava luku käsittelee sitä.

## Käytännössä

- **Laske radianssilla.** Pikseli, säde ja materiaalin säteily ovat
  radianssia; irradianssi syntyy vasta integroimalla.
- **Muista $\pi$:t.** Lambertin BRDF on $\rho/\pi$, ja vakioradianssin
  irradianssi on $\pi L$. Unohtunut tai ylimääräinen $\pi$ on yleisin
  syy liian kirkkaaseen tai tummaan kuvaan.
- **Tarkista energian säilyminen** numeerisesti jokaiselle uudelle
  BRDF:lle: suunta-albedo saa olla enintään 1.
- **Pintavalo ei ole pistevalo lähellä.** Käänteisen neliön laki
  pätee, kun etäisyys on vähintään viisinkertainen valon kokoon
  nähden.
- **Ajattele renderöintiyhtälöä sarjana**: suora valo, yksi
  heijastus, kaksi heijastusta. Monet optimoinnit käsittelevät termejä
  eri tavoin.

## Itsearviointi

- Osaat määritellä säteilytehon, irradianssin, intensiteetin ja
  radianssin ja selittää, miksi säteenseuranta laskee radianssia.
- Osaat luetella fysikaalisen BRDF:n ominaisuudet ja tarkistaa
  energian säilymisen numeerisesti.
- Osaat muuntaa avaruuskulman integraalin pinta-alan integraaliksi ja
  laskea pintavalon irradianssin.
- Osaat kirjoittaa renderöintiyhtälön, selittää sen rekursiivisen
  rakenteen ja perustella, miksi se ratkaistaan Monte Carlolla.
