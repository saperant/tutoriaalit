# Lomakkeet, reducer ja konteksti

Varauslomake on sovelluksen monimutkaisin näkymä: neljä kenttää,
validointi, lähetys palvelimelle, odotustila, virhe ja onnistuminen.
Kun tällaista tilaa hoidetaan erillisillä `useState`-muuttujilla, syntyy
mahdottomia yhdistelmiä, kuten "lähetetään" ja "valmis" yhtä aikaa.
Ratkaisu on mallintaa tila tilakoneena ja keskittää siirtymät
**reduceriin**. Luvussa 2 lomake luettiin `FormData`-oliosta
lähetyshetkellä; tässä kenttien arvot ovat Reactin tilassa, jotta
näkymä voi reagoida niihin joka näppäilyllä.

## Validointi

Validointi on puhdas funktio luonnoksesta virheisiin. Samaa funktiota
käyttää myös palvelin (luku 7): selaimen tarkistus palvelee käyttäjää,
mutta vain palvelimen tarkistukseen voi luottaa, koska pyynnön voi
lähettää ohi käyttöliittymän.

```{.typescript tiedosto="esimerkit/src/05-lomakkeet/varaus.ts" osa="tyypit"}
```

```{.typescript tiedosto="esimerkit/src/05-lomakkeet/varaus.ts" osa="validoi"}
```

Päivämäärät ovat ISO-muotoisia merkkijonoja (`2026-12-01`), joita voi
verrata suoraan. Kellonaika ja aikavyöhyke ovat oma kysymyksensä:
tuotannossa ajat tallennetaan palvelimelle UTC-aikaleimoina, ja
käyttöliittymä näyttää ne käyttäjän aikavyöhykkeessä (`Intl.DateTimeFormat`).

Selaimen `Intl`-rajapinta hoitaa muunkin kielestä riippuvan
muotoilun, joten sitä ei kirjoiteta itse:
`Intl.DateTimeFormat("fi-FI")` muotoilee päivämäärän (1.12.2026),
`Intl.NumberFormat` luvut ja valuutat (1 234,50 €),
`Intl.PluralRules` valitsee monikkomuodon ja `Intl.Collator`
aakkostaa ääkköset oikein. Tallennus- ja siirtomuoto pysyy kielestä
riippumattomana (ISO 8601, piste desimaalierottimena), ja muotoilu
tehdään vasta näkymässä.

## Tila erotelluksi unioniksi

Lomakkeen tila on eroteltu unioni (taito *TypeScript*), jossa jokaisella
vaiheella on juuri ne tiedot, jotka siinä ovat olemassa. Varaus-id on
vain valmiissa tilassa, virheilmoitus vain virhetilassa:

```{.typescript tiedosto="esimerkit/src/05-lomakkeet/varausReducer.ts" osa="tila"}
```

```{.dot otsikko="Lomakkeen tilakone. Nuolet ovat reducerin sallimat siirtymät; muut toiminnot eivät muuta tilaa."}
digraph {
  rankdir=LR; nodesep=0.5; ranksep=0.6;
  node [shape=ellipse];
  alku [shape=point, width=0.12];
  m [label="muokkaus"]; l [label="lahetys"];
  v [label="valmis", peripheries=2]; e [label="virhe"];
  alku -> m;
  m -> m [label="muuta;\nlaheta, kun\nvirheitä"];
  m -> l [label="laheta,\nkun kelpaa"];
  l -> v [label="onnistui"];
  l -> e [label="epaonnistui"];
  e -> m [label="muuta"];
  e -> l [label="laheta"];
}
```

Reducer on puhdas funktio `(tila, toiminto) → uusi tila`. Se päättää,
mitkä siirtymät ovat sallittuja: lähetyksen aikana kenttiä ei voi
muuttaa, ja myöhässä saapuva vastaus ei muuta jo valmista tilaa.
`never`-haara saa kääntäjän huomauttamaan, jos uusi toiminto jää
käsittelemättä.

```{.typescript tiedosto="esimerkit/src/05-lomakkeet/varausReducer.ts" osa="reducer"}
```

Koska reducer on puhdas funktio, sen testit eivät tarvitse Reactia,
DOM:ia eikä ajastimia:

```{.typescript tiedosto="esimerkit/src/05-lomakkeet/varausReducer.test.ts" osa="testi"}
```

## Lomakekomponentti

Komponentti kytkee reducerin näkymään `useReducer`-hookilla. Kentät
ovat kontrolloituja: arvo tulee tilasta ja jokainen muutos on toiminto.

```{.typescript tiedosto="esimerkit/src/05-lomakkeet/VarausLomake.tsx" osa="lomake"}
```

![Vaihe "muokkaus" virheellisen lähetyksen jälkeen.](kuvat/05-virheet.png){width=45%}&nbsp;&nbsp;&nbsp;&nbsp;
![Vaihe "lahetys".](kuvat/05-lahetys.png){width=45%}

Kuvissa lomake on kahdessa vaiheessa. Vasemmalla on vaihe "muokkaus"
virheellisen lähetyksen jälkeen: virheet ovat kenttien alla, ja fokus
on ensimmäisessä virheellisessä kentässä. Oikealla on vaihe "lahetys":
painike on pois käytöstä, ja sen teksti kertoo tilan.

Neljä ratkaisua ansaitsee huomion.

1. **Lähetys tapahtumankäsittelijässä.** Pyyntö on käyttäjän toiminnon
   seuraus, joten se lähetetään `onSubmit`-käsittelijässä. Jos lähetys
   käynnistettäisiin efektissä tilan muutoksesta, `StrictMode` ja
   uudelleenrenderöinnit voisivat lähettää sen kahdesti. Efektit ovat
   synkronointia varten (luku 6), eivät tapahtumia varten.
2. **`noValidate` ja oma validointi.** Selaimen omat virhekuplat eivät
   noudata sovelluksen kieltä ja ulkoasua, ja niiden ruudunlukijatuki
   vaihtelee. Siksi lomake validoidaan itse, ja selaimen tyypit
   (`type="date"`) jäävät syöttöavuksi.
3. **Saavutettavat virheet.** Virheellinen kenttä saa
   `aria-invalid`-attribuutin, ja virheteksti liitetään siihen
   `aria-describedby`-attribuutilla, joten ruudunlukija lukee sen
   kentän nimen jälkeen. Fokus siirretään ensimmäiseen virheelliseen
   kenttään. Malli on sama kuin taidon *HTML ja CSS* lomakkeissa;
   erona on, että virheet lasketaan selaimessa eikä sivua ladata.
4. **Arvot säilyvät virheessä.** Epäonnistuneen lähetyksen jälkeen
   käyttäjä ei kirjoita mitään uudelleen. Virheilmoitus on
   `role="alert"`-alueessa ja onnistuminen `role="status"`-alueessa.

Testi hakee kentän nimellä *ja kuvauksella*, eli täsmälleen niin kuin
ruudunlukija sen esittää:

```{.typescript tiedosto="esimerkit/src/05-lomakkeet/VarausLomake.test.tsx" osa="testi"}
```

## Konteksti

Kirjautunut käyttäjä, kieli ja teema tarvitaan monessa komponentissa
syvällä puussa. Niiden välittäminen propseina jokaisen välikomponentin
läpi (*prop drilling*) on työlästä. **Konteksti** välittää arvon koko
alipuulle:

```{.typescript tiedosto="esimerkit/src/05-lomakkeet/Kayttaja.tsx" osa="konteksti"}
```

Konteksti kääritään omaan hookiin, joka kertoo selvästi puuttuvasta
tarjoajasta. Kontekstin arvon muuttuminen renderöi kaikki sitä lukevat
komponentit, joten kontekstiin kuuluu harvoin muuttuva tieto. Usein
muuttuva jaettu tila (esim. ostoskori) kuuluu tilakirjastoon tai
useaan pieneen kontekstiin.

## Käytännössä

- **Tilakone mahdottomia tiloja vastaan.** Kun tilamuuttujia on monta ja
  niiden yhdistelmillä on sääntöjä, tila mallinnetaan erotelluksi
  unioniksi ja siirtymät reduceriin. Isommissa sovelluksissa
  tilakonekirjasto (XState) tuo lisäksi visualisoinnin.
- **Reducer on testattava logiikka.** Liiketoimintasäännöt puhtaisiin
  funktioihin, joita testataan ilman käyttöliittymää; komponentti on
  ohut kerros niiden päällä.
- **Validoi molemmissa päissä samalla koodilla.** Jaettu validointi
  (tai jaettu skeema, esim. Zod) pitää säännöt yhtenäisinä.
- **Kenttätason virheet tekstinä kentän yhteydessä,** ei pelkällä
  värillä. Lähetyksen aikana painike pois käytöstä ja teksti, joka
  kertoo tilan. Lomakekirjastot (React Hook Form, TanStack Form)
  hoitavat suurten lomakkeiden suorituskyvyn ja kirjanpidon.
- **Konteksti on riippuvuuksien välitystä, ei tilanhallintaa.** Hyvä
  käyttäjälle, kielelle, teemalle ja palveluille (API-asiakas). Ei
  hyvä nopeasti muuttuvalle datalle.

## Itsearviointi

- Osaat mallintaa lomakkeen tilan erotelluksi unioniksi ja kirjoittaa
  sille reducerin, joka estää mahdottomat siirtymät.
- Osaat toteuttaa saavutettavan validoinnin (`aria-invalid`,
  `aria-describedby`, fokus) ja testata sen.
- Osaat perustella, miksi lähetys kuuluu tapahtumankäsittelijään eikä
  efektiin.
- Osaat käyttää kontekstia oman hookin kautta ja tiedät sen
  suorituskykyhinnan.
