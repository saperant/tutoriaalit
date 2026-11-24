# Integraatiomallit

Gregor Hohpen ja Bobby Woolfin kirja *Enterprise Integration Patterns*
(2003) nimesi viestipohjaisen integraation rakennuspalikat: kanavat,
reitittimet, kääntäjät, pilkkojat, kokoojat ja niin edelleen. Mallit
ovat yhä integraatiokehysten (Apache Camel, Spring Integration) ja
pilvipalvelujen (AWS EventBridge, Azure Logic Apps) sanastoa. Tässä
luvussa mallit toteutetaan pieninä Java-funktioina ilman välittäjää,
jotta niiden ajatus näkyy.

## Viesti ja kanava

*Viesti* on otsakkeet ja runko. Otsakkeet kuljettavat reitityksen ja
jäljityksen tiedot (tyyppi, korrelaatiotunnus, lähde), runko itse
sisällön. *Kanava* on nimetty yhteys, jota pitkin viestit kulkevat:
jono tai aihe. Integraatiomallit ovat suodattimia kanavien välissä, ja
niistä kootaan *putkia ja suodattimia* (*pipes and filters*).

## Kääntäjä

Vanha tilausjärjestelmä lähettää tilaukset puolipisteillä erotettuina
riveinä. *Kääntäjä* (*message translator*) muuttaa ne yhteiseen
muotoon, jotta kaikkien vastaanottajien ei tarvitse tuntea vanhaa
muotoa:

```{.java tiedosto="esimerkit/viestit/src/main/java/fi/tutoriaalit/palvelut/viestit/integraatio/Mallit.java" osa="kaantaja"}
```

Kääntäjä on integraation korruption estokerros (luku 12). Jos
järjestelmiä on $n$ ja kukin kääntää suoraan kaikkien muiden muotoihin,
kääntäjiä tarvitaan $n(n-1)$. Yhteisen *kanonisen muodon* kanssa niitä
tarvitaan $2n$.

## Pilkkoja ja kokooja

*Pilkkoja* (*splitter*) jakaa koostetun viestin osiin, jotka voidaan
käsitellä erikseen, esimerkiksi tilauksen rivikohtaisiksi viesteiksi.
Jokaiseen osaan liitetään *korrelaatiotunnus* ja tieto osien määrästä:

```{.java tiedosto="esimerkit/viestit/src/main/java/fi/tutoriaalit/palvelut/viestit/integraatio/Mallit.java" osa="pilkkoja"}
```

*Kokooja* (*aggregator*) tekee päinvastoin: se kerää samaan
korrelaatiotunnukseen kuuluvat viestit ja julkaisee koosteen, kun
*valmistumisehto* täyttyy. Tässä ehto on "kaikki osat saapuneet";
muita tavallisia ehtoja ovat aikaraja ja "riittävän monta vastausta".

```{.java tiedosto="esimerkit/viestit/src/main/java/fi/tutoriaalit/palvelut/viestit/integraatio/Mallit.java" osa="kokooja"}
```

```{.java tiedosto="esimerkit/viestit/src/test/java/fi/tutoriaalit/palvelut/viestit/integraatio/MallitTest.java" osa="kokooja"}
```

Kokoojan tila on pysyvää: jos prosessi kaatuu, keskeneräiset koosteet
on löydettävä uudelleen. Siksi oikeat kokoojat tallentavat tilansa
tietokantaan, ja keskeneräisille koosteille on aikaraja, jonka
jälkeen ne julkaistaan vajaina tai siirretään tutkittaviksi.

## Reititin ja suodatin

*Sisältöön perustuva reititin* (*content-based router*) valitsee
kanavan viestin sisällön perusteella. *Suodatin* (*message filter*)
pudottaa viestit, joita vastaanottaja ei tarvitse:

```{.java tiedosto="esimerkit/viestit/src/main/java/fi/tutoriaalit/palvelut/viestit/integraatio/Mallit.java" osa="reititin"}
```

Koko putki: vanhan järjestelmän rivit käännetään, pilkotaan
riveiksi, nollarivit suodatetaan, ja jäljelle jäävät reititetään kotimaan
tai ulkomaan toimitukseen. Rivi, jota ei voi kääntää, päätyy
*kuolleiden kirjeiden kanavaan* (*dead letter channel*) eikä pysäytä
muita:

```{.java tiedosto="esimerkit/viestit/src/test/java/fi/tutoriaalit/palvelut/viestit/integraatio/MallitTest.java" osa="putki"}
```

## Muita malleja

| Malli | Käyttö |
|-------|--------|
| Kirjekuori (*envelope wrapper*) | kuljetuksen tiedot erillään sisällöstä |
| Lunastuskuitti (*claim check*) | suuri runko tallennetaan erikseen, viestissä vain viite |
| Salakuuntelu (*wire tap*) | kopio viesteistä valvontaan tai lokiin |
| Vastaanottajaluettelo (*recipient list*) | sama viesti laskettuun joukkoon kanavia |
| Hajauta ja kokoa (*scatter-gather*) | kysely monelle, vastausten kooste |
| Prosessinhallinta (*process manager*) | monivaiheisen prosessin tila ja ohjaus, ks. saga |
| Uudelleenjärjestäjä (*resequencer*) | epäjärjestyksessä tulleet viestit järjestykseen |
| Kanavasovitin (*channel adapter*) | tiedosto, sähköposti tai FTP viestikanavaksi |

## Missä mallit asuvat

Mallit voi toteuttaa kolmessa paikassa:

1. **Palvelun sisällä** omana koodina, kuten tässä luvussa. Selkeä,
   testattava ja riittävä useimpiin tarpeisiin.
2. **Integraatiokehyksessä** (Apache Camel, Spring Integration), joka
   tarjoaa mallit valmiina ja kymmenittäin kanavasovittimia
   (tiedostot, FTP, SAP, sähköposti).
3. **Keskitetyssä integraatioalustassa** (ESB, iPaaS). Tämä on
   perusteltua lähinnä valmisohjelmistojen yhdistämisessä. Omien
   palvelujen liiketoimintalogiikka ei kuulu sinne: SOA-aikakauden
   opetus on, että älykäs väylä muuttuu pullonkaulaksi (luku 5).

## Käytännössä

- **Nimeä mallit.** "Pilkotaan rivit ja kootaan korrelaatiotunnuksella"
  on täsmällisempi ja lyhyempi kuin sama asia kuvattuna.
- **Korrelaatiotunnus jokaiseen viestiin**, jotta pilkotut osat voi
  koota ja tapahtumaketjun jäljittää.
- **Kanoninen muoto ja kääntäjät reunoille.** Vanhan tai ulkoisen
  järjestelmän muoto ei saa levitä järjestelmän sisälle.
- **Kuolleiden kirjeiden kanava jokaiseen putkeen.** Yksi rikkinäinen
  viesti ei saa pysäyttää muita.
- **Hinnat:** jokainen vaihe on uusi paikka, jossa viesti voi jumittua
  tai kadota; kokoojan tila on pysyvää ja vaatii aikarajat; pitkä
  putki on vaikea jäljittää ilman korrelaatiotunnuksia.

## Itsearviointi

- Osaat nimetä ja toteuttaa kääntäjän, pilkkojan, kokoojan,
  reitittimen ja suodattimen.
- Osaat selittää korrelaatiotunnuksen ja kokoojan valmistumisehdon
  merkityksen.
- Osaat perustella kanonisen muodon ja kuolleiden kirjeiden kanavan.
- Osaat valita, toteutetaanko integraatio omana koodina,
  integraatiokehyksellä vai integraatioalustassa.
