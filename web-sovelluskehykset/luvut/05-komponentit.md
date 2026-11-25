# Komponentin rajapinta

Komponentti on kaikissa neljässä kehyksessä sama asia: nimetty,
uudelleenkäytettävä pala näkymää, jolla on oma tilansa ja **rajapinta**
ympäristöönsä. Rajapinta on se, mikä tekee komponentista enemmän kuin
funktion, joka tuottaa HTML:ää. Tässä luvussa luetaan sovelluksen kaksi
pienintä komponenttia neljällä kehyksellä ja katsotaan, miten tieto
kulkee niihin ja niistä pois.

```{.dot otsikko="Sovelluksen komponentit: tieto kulkee alas, tapahtumat ylös, ja jaettu tila ohittaa puun (luku 7)"}
digraph {
  rankdir=TB;
  S [label="Sovellus\nsuodatin (paikallinen tila)"];
  Y [label="Yhteenveto"];
  L [label="Lisayslomake\nnimi, kiire (paikallinen tila)"];
  F [label="SuodatinValinta"];
  R [label="TehtavaRivi × n"];
  T [label="jaettu tila:\ntehtävät, lataus", shape=cylinder];
  S -> Y; S -> L;
  S -> F [label="arvo ↓  muutos ↑"];
  S -> R [label="tehtävä ↓\nvaihda, poista ↑"];
  T -> S [style=dashed]; T -> Y [style=dashed]; T -> L [style=dashed];
}
```

## Tieto alas, tapahtumat ylös

Rivikomponentti saa vanhemmaltaan yhden tehtävän ja kertoo
vanhemmalle, kun käyttäjä merkitsee tehtävän valmiiksi tai poistaa
sen. Rivi ei itse muuta mitään: se ei tiedä, missä tehtävät ovat tai
miten ne tallennetaan. Tätä kutsutaan **yksisuuntaiseksi
tietovirraksi**, ja se on kaikkien neljän kehyksen suositus.

Reactissa rajapinta on funktion parametrit. Tapahtumat ovat
ominaisuuksia siinä missä tietokin: vanhempi antaa funktion, ja lapsi
kutsuu sitä.

```{.typescript tiedosto="esimerkit/react/src/TehtavaRivi.tsx" osa="rivi"}
```

Vuessa tieto ja tapahtumat ovat eri käsitteitä: `defineProps` kertoo,
mitä komponentti saa, ja `defineEmits`, mitä tapahtumia se lähettää.

```{.html tiedosto="esimerkit/vue/src/TehtavaRivi.vue"}
```

Angularissa rajapinta on luokan kenttiä: `input()` on tieto alas ja
`output()` tapahtuma ylös.

```{.typescript tiedosto="esimerkit/angular/src/app/tehtava-rivi.ts" osa="rivi"}
```

```{.html tiedosto="esimerkit/angular/src/app/tehtava-rivi.html"}
```

Sveltessä rajapinta on yksi `$props()`-olio, ja tapahtumat ovat
takaisinkutsuja kuten Reactissa.

```{.html tiedosto="esimerkit/svelte/src/TehtavaRivi.svelte"}
```

| Asia | React | Vue | Angular | Svelte |
|------|-------|-------|-------|--------|
| tieto alas | funktion parametri | `defineProps` | `input()` | `$props()` |
| tapahtuma ylös | takaisinkutsu propsina | `defineEmits`, `$emit` | `output()`, `emit` | takaisinkutsu propsina |
| rajapinnan tyyppi | TypeScript-rajapinta | tyyppiparametri | kenttien tyypit | TypeScript-rajapinta |
| luokka ehdollisesti | merkkijono | `:class="{…}"` | `[class.x]` | taulukko tai olio |

Erot ovat pinnallisia, mutta kaksi niistä kertoo kehyksen luonteesta.
React ja Svelte eivät erota tapahtumia tiedosta: funktio on arvo
muiden joukossa, ja rajapinta on yksi olio. Vue ja Angular antavat
tapahtumille oman käsitteensä, jolloin rajapinnasta näkee suoraan,
mikä on syöte ja mikä tuloste, ja kehyksen työkalut osaavat näyttää
tapahtumat erikseen.

Angularin listauksessa näkyy edellisen luvun isäntäelementti.
Valitsin `li[app-tehtava-rivi]` tarkoittaa, että komponentti ei luo
omaa elementtiään vaan liittyy vanhemman kirjoittamaan `<li>`:hin.
Elementin luokat sidotaan `host`-kentässä, koska mallipohja kuvaa vain
elementin sisällön.

## Kaksisuuntainen sidos

Suodatinvalinta on lomakekentän kaltainen komponentti: sillä on arvo,
jonka vanhempi omistaa ja jota käyttäjä muuttaa. Reactissa tämä
kirjoitetaan aina auki, arvo alas ja muutos ylös:

```{.typescript tiedosto="esimerkit/react/src/SuodatinValinta.tsx" osa="suodatin"}
```

Vanhempi kytkee molemmat päät itse:
`<SuodatinValinta arvo={suodatin} onMuutos={setSuodatin} />`.

Muissa kolmessa kehyksessä samalle parille on lyhennysmerkintä,
**kaksisuuntainen sidos**. Vuessa komponentti määrittelee mallin ja
vanhempi kirjoittaa `v-model`:

```{.html tiedosto="esimerkit/vue/src/SuodatinValinta.vue"}
```

Angularissa `model()` tekee saman, ja vanhemman merkintä on
`[(arvo)]="suodatin"`. Sulkuyhdistelmä kertoo itse, mitä se on:
hakasulkeet arvolle alas ja kaarisulkeet tapahtumalle ylös.

```{.typescript tiedosto="esimerkit/angular/src/app/suodatin-valinta.ts"}
```

```{.html tiedosto="esimerkit/angular/src/app/suodatin-valinta.html"}
```

Sveltessä ominaisuus merkitään sidottavaksi, ja vanhempi kirjoittaa
`bind:arvo={suodatin}`:

```{.html tiedosto="esimerkit/svelte/src/SuodatinValinta.svelte"}
```

Kaksisuuntainen sidos **ei ole eri tietovirta**. Jokaisessa kolmessa
kehyksessä se on lyhennys täsmälleen sille, minkä React kirjoittaa
auki: arvo alas, muutostapahtuma ylös. Koodin kommenteissa on
mainittu, mihin pariin kehys merkinnän purkaa (`modelValue` ja
`update:modelValue`, `arvo` ja `arvoChange`).

Aito kaksisuuntainen sidonta, jossa lapsi muuttaa vanhemman tilaa
suoraan ja kehys etsii muutokset, oli AngularJS:n tunnetuin ominaisuus
ja sen suurten sovellusten suurin ongelma: kun mikä tahansa komponentti
voi muuttaa mitä tahansa, virheen syytä ei löydä lukemalla. Reactin
yksisuuntaisuus oli vastaus siihen. Nykyiset lyhennysmerkinnät
säilyttävät yksisuuntaisuuden ja poistavat vain kirjoitusvaivan.

Hinta on, että sidoksen takana oleva muutos ei näy koodissa.
`setSuodatin` on funktio, jonka kutsut voi etsiä ja johon voi asettaa
keskeytyskohdan. `v-model` on merkintä mallipohjassa.

## Sisällön välittäminen

Komponentille voi antaa myös näkymän palan, jonka se sijoittaa
johonkin kohtaan itseään: painikkeen sisällön, kortin otsikon tai
taulukon rivin ulkoasun. Tehtävälistassa tätä ei tarvita, mutta käsite
on jokaisessa kehyksessä.

| Asia | React | Vue | Angular | Svelte |
|------|--------|------|--------|--------|
| oletussisältö | `children` | `<slot>` | `<ng-content>` | `children`-leike |
| nimetty kohta | props, jonka arvo on JSX:ää | nimetty `<slot>` | `select`-valitsin | leike (`{#snippet}`) |

Reactissa välitettävä sisältö on tavallinen arvo, koska JSX on
lauseke. Mallipohjakehyksissä sille tarvitaan oma rakenne. Tämä on
luvun 4 ero pienoiskoossa.

## Käytännössä

- **Suunnittele rajapinta ennen toteutusta.** Mitä komponentti
  tarvitsee ja mistä se ilmoittaa? Hyvä rajapinta on pieni ja puhuu
  sovellusalueen sanoilla (`tehtava`, `poista`), ei toteutuksen
  (`onButtonClick`).
- **Lapsi ei muuta saamaansa tietoa.** Jos rivi asettaisi itse
  `tehtava.valmis = true`, muutos toimisi osassa kehyksistä ja jäisi
  huomaamatta osassa, eikä vanhempi tietäisi siitä missään. Lapsi
  ilmoittaa, omistaja muuttaa.
- **Kaksisuuntainen sidos kuuluu kenttien kaltaisille komponenteille.**
  Valinta, liukusäädin ja päivämääräkenttä ovat luontevia. Jos
  komponentti tekee muutoksen yhteydessä muutakin kuin välittää arvon,
  kirjoita tapahtuma auki.
- **Pidä komponentit tyhminä niin pitkälle kuin voi.** Rivi ja
  suodatin eivät tiedä tilanhallinnasta mitään, joten ne voi testata
  ja siirtää toiseen näkymään sellaisinaan. Tila kuuluu harvoihin
  ylätason komponentteihin.

## Itsearviointi

- Osaat kirjoittaa saman komponentin rajapinnan neljällä kehyksellä:
  tieto alas ja tapahtuma ylös.
- Osaat selittää, mitä kaksisuuntainen sidos nykykehyksissä on ja
  miksi se ei riko yksisuuntaista tietovirtaa.
- Osaat kertoa, miksi lapsikomponentti ei saa muuttaa saamaansa oliota.
- Osaat nimetä tavan välittää näkymän pala komponentille kussakin
  kehyksessä.
