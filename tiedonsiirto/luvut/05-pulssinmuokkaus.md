# Pulssinmuokkaus ja symbolien välinen häiriö

Symboli lähetetään pulssina, ja pulssin muoto ratkaisee kaksi asiaa:
kuinka leveää kaistaa signaali vie ja häiritsevätkö peräkkäiset
symbolit toisiaan vastaanottimessa. Suorakaidepulssi on lyhyt ajassa
mutta leveä taajuudessa. Kapeakaistainen pulssi taas on pitkä ajassa,
joten peräkkäiset pulssit menevät päällekkäin. Päällekkäisyys ei
haittaa, jos jokainen pulssi on nolla muiden symbolien näytehetkillä.
Tämä on **Nyquistin ehto**, ja sen täyttävät pulssit mahdollistavat
kapean kaistan ilman **symbolien välistä häiriötä** (ISI, *intersymbol
interference*).

## Nyquistin ehto ja korotettu kosini

Pulssi $p(t)$ ei aiheuta ISI:ä, jos $p(kT) = 0$ kaikilla
$k \ne 0$. Kapein tällainen pulssi on $\operatorname{sinc}(t/T)$,
jonka kaista on $1/(2T)$, mutta sen hännät vaimenevat hitaasti
($1/t$). Käytännön ratkaisu on **korotettu kosini** (RC, *raised
cosine*), jonka kaista on $(1+\beta)/(2T)$. Roll-off-kerroin
$0 \le \beta \le 1$ määrää, kuinka paljon ylimääräistä kaistaa
käytetään nopeammin vaimenevien häntien hyväksi.

Lähettimen ja vastaanottimen suotimet jaetaan niin, että kummassakin
on **juurikorotettu kosini** (RRC). Erikseen RRC ei täytä Nyquistin
ehtoa, mutta kahden RRC:n konvoluutio on RC. Samalla vastaanottimen
suodin on lähetyspulssin **sovitettu suodin**, joka maksimoi
signaali-kohinasuhteen (seuraava osio).

```{.python tiedosto="esimerkit/05-nyquist.py" osa="pulssit"}
```

ISI mitataan summana muiden symbolien näytehetkillä olevista pulssin
arvoista suhteessa huippuun. Se on pahimman tapauksen häiriö, jonka
naapurisymbolit voivat yhdessä tuottaa.

```{.python tiedosto="esimerkit/05-nyquist.py" osa="isi"}
```

Kaistan voi mitata kahdella tavalla: pulssin spektri on tarkalleen
nolla taajuuden $(1+\beta)/(2T)$ yläpuolella, ja 99 %:n kaista kertoo,
kuinka kapealla kaistalla lähes kaikki teho kulkee.

```{.python tiedosto="esimerkit/05-nyquist.py" osa="kaista"}
```

```{.tuloste tiedosto="esimerkit/05-nyquist.odotettu"}
```

Yksinään RRC tuottaa ISI:n 0,34, mutta sovitetun suotimen jälkeen ISI
on 0,008. Jäännös johtuu pulssin katkaisemisesta 16 symbolin
mittaiseksi. Pidempi suodin pienentää sitä, mutta lisää viivettä ja
laskentaa. Sinc-pulssi ja RC ovat näytehetkillä tarkasti nollia.

## Silmäkuvio ja ajoitusherkkyys

Nyquistin ehto koskee vain tarkkoja näytehetkiä. Jos vastaanotin ottaa
näytteen hieman väärään aikaan, naapurisymbolien häntien arvot
summautuvat näytteeseen. **Silmäkuvio** piirtää signaalin päällekkäin
symbolin mittaisina pätkinä. Avoin silmä tarkoittaa, että päätösraja
(tässä nolla) on selvästi erillään kaikista käyristä, ja silmän
leveys kertoo, kuinka paljon ajoitusvirhettä siedetään.

![Sovitetun suotimen lähtö silmäkuviona BPSK:lla kahdella
roll-off-kertoimella. Kun $\beta$ on pieni, käyrät hajoavat näytehetken
ympärillä laajalle; suurella $\beta$:lla silmä on auki leveämmältä
alueelta.](kuvat/silma.png){width=100%}

```{.python tiedosto="esimerkit/05-silma.py" osa="aukeama"}
```

```{.tuloste tiedosto="esimerkit/05-silma.odotettu"}
```

Aukeama on pienin etäisyys päätösrajaan, ja negatiivinen arvo
tarkoittaa, että silmä on kiinni: jokin symbolijono kääntää päätöksen
ilman kohinaakin. Sinc-pulssin silmä sulkeutuu jo neljänneksen
symbolin ajoitusvirheellä. Pienellä $\beta$:lla säästetään kaistaa,
mutta symbolitahdistuksen on oltava tarkka (luku 8).

## Sovitettu suodin

Valkoisessa kohinassa paras lineaarinen vastaanottosuodin on lähetetyn
pulssin aikakäännetty kompleksikonjugaatti, **sovitettu suodin**. Se
maksimoi näytehetken signaali-kohinasuhteen, ja maksimi on
$E_s/N_0$ riippumatta pulssin muodosta. Muut suotimet menettävät osan
signaalista tai päästävät läpi ylimääräistä kohinaa. Sen lisäksi ne
tuottavat ISI:ä, koska RRC:n ja niiden konvoluutio ei ole
Nyquist-pulssi.

```{.python tiedosto="esimerkit/05-sovitettu.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/05-sovitettu.odotettu"}
```

Butterworth-alipäästö häviää signaali-kohinasuhteessa vain 0,14 dB,
mutta sen aiheuttama ISI 0,15 on vakavampi ongelma: se sulkee silmää
kohinasta riippumatta. Siksi käytännön vastaanottimet toteuttavat
sovitetun RRC-suotimen digitaalisesti. Analoginen suodin ennen
A/D-muunninta on väljä, ja sen tehtävä on vain estää laskostuminen.

## Käytännössä

- **Valitse $\beta$ kaistan ja kestävyyden välillä.** Tyypillisiä
  arvoja ovat 0,2–0,35 (DVB-S2 0,2, 0,25 tai 0,35; monet
  yksikantoaaltolinkit 0,25–0,5). Pieni $\beta$ säästää kaistaa, mutta
  vaatii pitkät suotimet ja tarkan ajoituksen.
- **Jaa suodatus RRC + RRC.** Lähettimen RRC rajaa kaistan, ja
  vastaanottimen RRC on sovitettu suodin. Yhdessä ne ovat RC, eli
  ISI-vapaat.
- **Mitoita suotimen pituus.** 8–16 symbolin pituinen RRC on tavallinen
  kompromissi. Tarkista katkaisun aiheuttama ISI ja kaistan ulkopuolinen
  vuoto simuloimalla.
- **Normita pulssin energia.** Kun $\sum h^2 = 1$, sovitetun suotimen
  lähdön näyte on suoraan symboli, ja kohinan varianssi on $N_0$. Tämä
  tekee luvun 6 kalibroinnista yksinkertaisen.
- **Piirrä silmäkuvio.** Se paljastaa ISI:n, väärän näytehetken ja
  epälineaarisuudet nopeammin kuin bittivirhesuhde.

## Itsearviointi

- Osaat selittää Nyquistin ehdon ja miksi päällekkäiset pulssit eivät
  välttämättä häiritse toisiaan.
- Osaat toteuttaa RC- ja RRC-pulssit ja mitata niiden ISI:n ja kaistan.
- Osaat tulkita silmäkuvion ja selittää roll-off-kertoimen vaikutuksen
  ajoitusherkkyyteen.
- Osaat perustella, miksi sovitettu suodin on paras vastaanottosuodin,
  ja laskea muiden suotimien SNR-menetyksen ja ISI:n.
