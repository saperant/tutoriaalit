# Kohina, SNR ja bittivirhesuhde

Vastaanottimen termisestä kohinasta alkaen useimmat kohinalähteet ovat
yhteensä hyvin kuvattavissa **additiivisena valkoisena Gaussin
kohinana** (AWGN): kohina lisätään signaaliin, sen spektri on tasainen
ja arvot ovat normaalijakautuneita. AWGN-kanava on tiedonsiirron
vertailukohta. Sen yli lasketaan modulaatioiden teoreettiset
virhetodennäköisyydet, sitä vastaan tarkistetaan simulaatiot, ja sen
kapasiteetti on Shannonin raja. Tässä luvussa kalibroidaan kohina
oikein, verrataan simulaatioita teoriaan ja katsotaan, mitä häipyvä
kanava muuttaa.

## Eb/N0, Es/N0 ja SNR

Kolme suuretta kuvaa samaa asiaa eri näkökulmista:

| Suure | Määritelmä | Käyttö |
|--------|------------------------------|----------------------|
| $E_b/N_0$ | bitin energia / kohinan tehotiheys | modulaatioiden ja koodien vertailu |
| $E_s/N_0$ | symbolin energia / kohinan tehotiheys, $= k\,E_b/N_0$ | konstellaation virhetodennäköisyys |
| SNR | signaalin teho / kohinan teho tietyllä kaistalla | mittalaitteet, linkkibudjetti |

$E_b/N_0$ on oikea vertailuyksikkö, koska se laskee energian siirrettyä
tietobittiä kohti: 16-QAM ja BPSK samalla $E_b/N_0$:lla käyttävät
saman energian bittiä kohti. SNR riippuu siitä, millä kaistalla kohinaa
mitataan. Kun signaalissa on `sps` näytettä symbolia kohti ja kohina
lisätään näytteisiin, näytekohtainen SNR on $E_s/N_0 - 10\log_{10}
\text{sps}$ dB. Ylinäytteistetty signaali näyttää siis
kohinaisemmalta kuin se on, koska suurin osa kohinasta on signaalin
kaistan ulkopuolella, ja sovitettu suodin poistaa sen.

```{.python tiedosto="esimerkit/06-awgn.py" osa="muunnokset"}
```

Vastaanotetun signaalin laatu mitataan päätöshetken näytteistä
**EVM**:nä (*error vector magnitude*): virhevektorin keskimääräisen
tehon ja symbolien tehon suhteena. AWGN-kanavassa $1/\text{EVM}^2$ on
mitattu $E_s/N_0$.

```{.python tiedosto="esimerkit/06-awgn.py" osa="mittaus"}
```

```{.tuloste tiedosto="esimerkit/06-awgn.odotettu"}
```

Mitattu arvo osuu tavoitteeseen, eli kohina on kalibroitu oikein. Tämä
tarkistus kannattaa tehdä jokaisen uuden simulaation alussa, koska
kohinan tason virhe siirtää kaikkia tuloksia, eikä sitä huomaa
muuten kuin vertaamalla teoriaan.

## Teoreettinen bittivirhesuhde

BPSK:n päätösmuuttuja on $\pm\sqrt{E_b}$ plus kohina, jonka varianssi
on $N_0/2$. Virhe tapahtuu, kun kohina ylittää etäisyyden
päätösrajaan:

$$P_b = Q\Bigl(\sqrt{2E_b/N_0}\Bigr),\qquad
  Q(x) = \tfrac12 \operatorname{erfc}\bigl(x/\sqrt2\bigr).$$

QPSK on kaksi rinnakkaista BPSK:ta, joten sen bittivirhesuhde on sama.
Gray-koodatun $M$-QAM:n ja $M$-PSK:n bittivirhesuhteelle saadaan
lähimpien naapurien likiarvot:

$$P_b^\text{QAM} \approx \frac{4}{k}\Bigl(1-\frac{1}{\sqrt M}\Bigr)
  Q\Bigl(\sqrt{\tfrac{3k}{M-1}\,E_b/N_0}\Bigr),\qquad
  P_b^\text{PSK} \approx \frac{2}{k}\,
  Q\Bigl(\sqrt{2kE_b/N_0}\,\sin\tfrac{\pi}{M}\Bigr).$$

```{.python tiedosto="esimerkit/06-ber.py" osa="teoria"}
```

Simulaatio lähettää satunnaisia symboleja, lisää kohinan ja tekee
päätöksen lähimmän pisteen mukaan. Se jatkuu, kunnes virheitä on 400,
jolloin tuloksen suhteellinen keskihajonta on noin 5 % (luku 11).

```{.python tiedosto="esimerkit/06-ber.py" osa="simuloi"}
```

```{.python tiedosto="esimerkit/06-ber.py" osa="vertaa"}
```

```{.tuloste tiedosto="esimerkit/06-ber.odotettu"}
```

Kaikki suhteet ovat yhden luokkaa satunnaisvaihtelun rajoissa.
Likiarvokaavat ovat tarkkoja tässä alueessa. Hyvin pienellä
$E_b/N_0$:lla ne alkavat poiketa, koska kauempana olevat naapurit
alkavat vaikuttaa.

![Teoreettinen bittivirhesuhde AWGN-kanavassa ja BPSK:lle
Rayleigh-häipymässä. Jokainen kaksi lisäbittiä symbolia kohti maksaa
noin 4 dB lisää $E_b/N_0$:aa samaan virhesuhteeseen. Häipyvässä
kanavassa virhesuhde laskee vain kertaluokan kymmentä desibeliä
kohti.](kuvat/ber.png){width=100%}

## Shannonin raja

Taito *Tietoliikennetekniikka* esitteli Shannonin kapasiteetin
$C = B\log_2(1 + \text{SNR})$. Kun siirtonopeus on $\eta$ bittiä
sekunnissa hertsiä kohti, $\text{SNR} = \eta\,E_b/N_0$, ja virheetön
siirto on mahdollinen vain, jos

$$\frac{E_b}{N_0} > \frac{2^\eta - 1}{\eta}.$$

Kun $\eta \to 0$, raja lähestyy arvoa $\ln 2$ eli $-1{,}59$ dB:ä: sen
alapuolella mikään menetelmä ei siirrä tietoa luotettavasti, kuinka
paljon kaistaa tahansa käytettäisiin.

```{.python tiedosto="esimerkit/06-kapasiteetti.py" osa="raja"}
```

```{.tuloste tiedosto="esimerkit/06-kapasiteetti.odotettu"}
```

Koodaamattomat modulaatiot jäävät 8,5–10,5 dB Shannonin rajasta, kun
tavoite on $10^{-6}$. Tämä väli on kanavakoodauksen pelivara: nykyiset
LDPC- ja turbokoodit pääsevät alle desibelin päähän rajasta (luku 10).
Linkkibudjetissa (taito *Tietoliikennetekniikka*) tarvittava
$E_b/N_0$ otetaan tällaisesta taulukosta, ja siihen lisätään
toteutushäviöt ja marginaali.

## Häipyvä kanava

Radiokanavassa signaali saapuu monta reittiä pitkin, ja reittien
summa vaihtelee, kun vastaanotin liikkuu. Jos reittien viive-erot ovat
pieniä symbolin kestoon nähden, kanava kertoo signaalin yhdellä
kompleksiluvulla $h$, joka on **Rayleigh-häipymässä** normaalijakautunut
nollakeskiarvoinen kompleksiluku. Kun $|h|$ on pieni, signaali hukkuu
kohinaan hetkellisesti, vaikka keskimääräinen $E_b/N_0$ olisi hyvä.

Ratkaisu on **diversiteetti**: useampi itsenäisesti häipyvä kopio
samasta signaalista, esimerkiksi kahdesta antennista. Optimaalinen
yhdistely (*maximum ratio combining*, MRC) painottaa kunkin haaran
sen kanavakertoimen konjugaatilla.

```{.python tiedosto="esimerkit/06-rayleigh.py" osa="teoria"}
```

```{.python tiedosto="esimerkit/06-rayleigh.py" osa="simuloi"}
```

```{.tuloste tiedosto="esimerkit/06-rayleigh.odotettu"}
```

Häipyvässä kanavassa BPSK tarvitsee 20 dB:llä saman virhesuhteen, jonka
AWGN-kanava antaa noin 6 dB:llä, ja 10 dB:n lisäys parantaa
virhesuhdetta vain kymmenkertaisesti. Toinen antenni muuttaa
kaltevuuden toisen asteen käyräksi: 20 dB:llä virhesuhde paranee yli
sata kertaa. Kahden antennin tuloksessa on vain noin 50 virhettä, joten
sen 25 %:n ero teoriaan on vielä satunnaisvaihtelua. Muut
diversiteetin muodot ovat aikadiversiteetti (koodaus ja lomitus, luku
10) ja taajuusdiversiteetti (OFDM ja koodaus, luku 7).

## Käytännössä

- **Kalibroi kohina ja tarkista se mittaamalla.** Normita
  konstellaatio ja pulssi, laske $N_0$ suureesta $E_b/N_0$ ja tarkista
  tulos EVM:llä. Useimmat simulaatiovirheet ovat kohinan tason
  virheitä.
- **Vertaa simulaatiota teoriaan aina kun voit.** Kun koko ketju
  (pulssit, sovitettu suodin, tahdistus) on mukana, ero teoriaan on
  **toteutushäviö**. Se on hyvässä vastaanottimessa alle 1 dB.
- **Käytä $E_b/N_0$:aa, kun vertaat modulaatioita tai koodeja.**
  Raportoi samalla, mitä suuretta käytät: 6 dB:n ero 16-QAM:n $E_b/N_0$:n
  ja $E_s/N_0$:n välillä on yleinen sekaannus.
- **Älä mitoita linkkiä AWGN-käyrällä, jos kanava häipyy.** Häipyvässä
  kanavassa tarvitaan diversiteettiä, koodausta tai kymmenien
  desibelien marginaali.

## Itsearviointi

- Osaat muuntaa $E_b/N_0$:n, $E_s/N_0$:n ja näytekohtaisen SNR:n
  toisikseen ja kalibroida simulaation kohinan.
- Osaat laskea BPSK:n, QPSK:n, $M$-PSK:n ja $M$-QAM:n teoreettisen
  bittivirhesuhteen ja verrata simulaatiota siihen.
- Osaat laskea Shannonin rajan spektritehokkuudesta ja arvioida
  koodaamattoman modulaation etäisyyden siitä.
- Osaat simuloida Rayleigh-häipymää ja selittää, miksi diversiteetti
  muuttaa virhesuhdekäyrän kaltevuutta.
