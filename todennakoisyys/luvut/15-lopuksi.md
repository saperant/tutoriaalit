# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

- **Laske ja simuloi.** Kaava antaa tarkan vastauksen ja simulaatio
  tarkistuksen. Kun ne eroavat, virhe on löytynyt.
- **Kysy lähtötaso.** Havainnon merkitys riippuu siitä, kuinka yleinen
  ilmiö on (Bayes).
- **Epäile riippumattomuutta.** Yhteiset syyt tekevät harvinaisista
  yhteisvioista yleisiä ja luottamusväleistä liian kapeita.
- **Summaa varianssit.** Riippumattomat epävarmuudet ja kohinat
  kasautuvat kuten $\sqrt{n}$.
- **Älä päättele syytä korrelaatiosta.** Piirrä hajontakuvio, etsi
  sekoittava tekijä ja katso regression jäännökset.
- **Ilmoita epävarmuus.** Jokaisen arvion rinnalle kuuluu keskivirhe
  tai luottamusväli.
- **Varo häntiä.** Vasteajoille ja muille raskashäntäisille suureille
  käytä mediaania ja persentiilejä, älä keskiarvoa.
- **Päätä analyysi ennen dataa.** Kurkkiminen ja monivertailu
  tuottavat vääriä löydöksiä.
- **Kiinnitä siemen.** Toistettava simulaatio on testattava
  simulaatio.

## Yhteenveto menetelmistä

| Kysymys | Menetelmä | Luku |
|---------|-----------|------|
| Kuinka todennäköistä? | luettelo, komplementti, simulaatio | Tapahtumat |
| Mitä havainto kertoo? | Bayesin kaava | Ehdollinen todennäköisyys |
| Montako tapahtumaa? | binomi, geometrinen, Poisson | Diskreetit jakaumat |
| Kuinka kauan? | eksponentti, normaali | Jatkuvat jakaumat |
| Paljonko keskimäärin? | lineaarisuus, indikaattorit | Odotusarvo ja varianssi |
| Vaihtelevatko yhdessä? | kovarianssi, korrelaatio, regressio | Kaksi muuttujaa |
| Kuinka tarkka keskiarvo? | $\sigma/\sqrt{n}$, raja-arvolause | Raja-arvolauseet |
| Kuinka paljon kohinaa? | SNR, varianssien summa | Kohina |
| Miten arvotaan? | käänteisfunktio, hylkäys | Satunnaisluvut |
| Ei kaavaa? | Monte Carlo, ositus | Monte Carlo |
| Mikä parametri? | ML, luottamusväli, bootstrap | Estimointi |
| Onko ero todellinen? | z-testi, permutaatiotesti, voima | Hypoteesitestaus |
| Mitä viive kertoo? | persentiilit, bootstrap | Mittausten tulkinta |

## Jatkotaidot

- *Digitaalinen tiedonsiirto*: kohina, signaali-kohinasuhde ja
  bittivirhesuhde digitaalisissa modulaatioissa.
- *Lineaarialgebra* ja *Numeeriset menetelmät*: pienimmän neliösumman
  sovitus usealle selittäjälle, kovarianssimatriisi ja
  pääkomponentit sekä sovituksen numeerinen luotettavuus.
- *Säteenseuranta ja fysikaalinen valaistus*: Monte Carlo -integrointi
  ja tärkeysotanta renderöintiyhtälön ratkaisemiseen.
- *Arkkitehtuurin mallinnus ja suunnittelutilan tutkiminen*:
  suorituskyvyn mallit, jonoteoria ja simulaatioiden tilastollinen
  tulkinta.
- *Tietoliikennetekniikka*: M/M/1-jono, Littlen laki ja
  kanavanvarauksen simulaatiot.
- *Suorituskyvyn analyysi ja optimointi*: vertailuajojen mittaaminen
  ja tulkinta.

## Lähteet ja lisälukemista

- Charles M. Grinstead ja J. Laurie Snell: *Introduction to
  Probability*. American Mathematical Society; vapaasti saatavilla
  GNU Free Documentation License -lisenssillä.
- David Diez, Mine Çetinkaya-Rundel ja Christopher Barr: *OpenIntro
  Statistics*. OpenIntro (CC BY-SA 3.0).
- Allen B. Downey: *Think Stats* ja *Think Bayes*. Green Tea Press
  (CC BY-NC-SA 4.0). Tilastotiede ja Bayes-päättely ohjelmoijalle.
- Eric Lehman, F. Thomson Leighton ja Albert R. Meyer: *Mathematics for
  Computer Science*. MIT, avoin oppikirja (CC BY-SA 3.0). Osa IV
  käsittelee todennäköisyyttä.
- NumPy-dokumentaatio: *Random sampling* (`numpy.random`) ja
  *Statistics*.
- Jeffrey Dean ja Luiz André Barroso: ”The Tail at Scale”.
  *Communications of the ACM* 56(2), 2013. Häntäviiveen vahvistuminen
  ja varapyynnöt.
- Ron Kohavi, Diane Tang ja Ya Xu: *Trustworthy Online Controlled
  Experiments*. Cambridge University Press 2020. A/B-testauksen
  käytännöt ja sudenkuopat.

## Lisenssi

Tämä tutoriaali on lisensoitu Creative Commons Nimeä–JaaSamoin 4.0
Kansainvälinen -lisenssillä (CC BY-SA 4.0). Esimerkkikoodi on
vapaasti käytettävissä samoin ehdoin.
