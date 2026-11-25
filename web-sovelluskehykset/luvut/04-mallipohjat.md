# Mallipohjat ja JSX

Näkyvin ero kehysten välillä on se, miten näkymä kirjoitetaan.
Reactissa HTML:n näköinen koodi on JavaScriptin seassa. Angularissa se
on omassa tiedostossaan. Vuessa ja Sveltessä se on samassa tiedostossa
mutta omassa lohkossaan. Ero ei ole kosmeettinen: sen takana on kaksi
eri vastausta kysymykseen, **onko näkymän kuvaus ohjelmakoodia vai
oma, rajattu kielensä**.

## Sama näkymä neljästi

Sovelluksen päänäkymässä on kaikki mallipohjan perusrakenteet: lapsi-
komponentit, kolmihaarainen ehto latauksen tilasta, lista ja
tapahtumankäsittelijät. Reactissa näkymä on komponenttifunktion
palauttama lauseke:

```{.typescript tiedosto="esimerkit/react/src/Sovellus.tsx" osa="sovellus"}
```

Vuessa sama on mallipohja, HTML:ää, johon on lisätty direktiivejä
(`v-if`, `v-for`) ja sidoksia (`:` arvolle, `@` tapahtumalle):

```{.html tiedosto="esimerkit/vue/src/Sovellus.vue" osa="pohja"}
```

Angularissa mallipohja on oma tiedostonsa. Ohjausrakenteet ovat
lohkoja (`@if`, `@for`, `@switch`), ja sidoksen suunta näkyy
sulkeista: hakasulkeet vievät arvon elementille, kaarisulkeet tuovat
tapahtuman sieltä:

```{.html tiedosto="esimerkit/angular/src/app/sovellus.html"}
```

Sveltessä komponenttitiedosto on HTML:n laajennus: merkintä on
tiedoston päätasolla ja ohjausrakenteet ovat aaltosulkulohkoja:

```{.html tiedosto="esimerkit/svelte/src/Sovellus.svelte" osa="pohja"}
```

Rakenne on kaikissa sama, ja sen voi lukea rivi riviltä rinnakkain:

| Asia | React | Vue | Angular | Svelte |
|------|-------|-----|---------|--------|
| teksti | `{x}` | `{{ x }}` | `{{ x() }}` | `{x}` |
| attribuutti | `disabled={x}` | `:disabled="x"` | `[disabled]="x()"` | `disabled={x}` |
| tapahtuma | `onClick={f}` | `@click="f"` | `(click)="f()"` | `onclick={f}` |
| ehto | `x && <p/>`, `? :` | `v-if`, `v-else` | `@if`, `@else` | `{#if}`, `{:else}` |
| lista | `xs.map(…)` | `v-for` | `@for` | `{#each}` |
| avain | `key={t.id}` | `:key="t.id"` | `track t.id` | `(t.id)` |

Taulukon syntaksi on tämän hetken yksityiskohta. Angularin lohkot
tulivat versiossa 17 vanhojen `*ngIf`- ja `*ngFor`-direktiivien tilalle,
ja Svelten tapahtumasyntaksi muuttui versiossa 5. Rivit sen sijaan
ovat pysyneet samoina: jokaisessa kehyksessä on jokin tapa tehdä nämä
kuusi asiaa.

## JSX on JavaScriptiä

JSX ei ole mallipohjakieli. `<p className="tila">…</p>` on toinen
kirjoitusasu funktiokutsulle, joka luo luvun 3 virtuaalisen solmun.
Siitä seuraa kaikki muu:

- **Ohjausrakenteet ovat JavaScriptin omia.** Ehto on `&&` tai
  ehdollinen lauseke, lista on `map`. Uutta kieltä ei ole, ja kaikki,
  minkä JavaScriptillä voi tehdä, on käytössä: näkymän osan voi
  sijoittaa muuttujaan, palauttaa funktiosta tai koota silmukassa.
- **TypeScript tarkistaa näkymän suoraan.** Komponentin ominaisuudet
  ovat funktion parametreja, joten väärä tyyppi tai puuttuva ominaisuus
  on tavallinen käännösvirhe. Erillistä tarkistinta ei tarvita, ja
  editorin uudelleennimeäminen toimii näkymän läpi.
- **Nimet ovat DOM-rajapinnan nimiä**, eivät HTML:n: `className`,
  `htmlFor`, `onChange`. HTML:ää ei voi liittää sellaisenaan.
- **Kääntäjä ei tiedä, mikä on staattista.** Koska näkymä on vapaata
  koodia, kehys ei voi päätellä etukäteen, mitkä osat eivät koskaan
  muutu. Siksi React laskee ja vertaa oletuksena kaiken.

## Mallipohja on rajattu kieli

Vuen, Angularin ja Svelten mallipohjissa voi tehdä vain sen, mitä
mallipohjakieli sallii: sitoa arvoja, toistaa ja ehdollistaa. Rajoitus
on ominaisuus.

- **Kääntäjä näkee rakenteen.** Mallipohjasta erottaa käännösvaiheessa,
  mikä on kiinteää HTML:ää ja mikä riippuu tilasta. Vuen kääntäjä
  merkitsee muuttuvat kohdat, jolloin vertailu ohittaa kaiken muun.
  Angularin kääntäjä tuottaa mallipohjasta käskyjonon, joka päivittää
  vain sidokset. Svelte tuottaa suoraan DOM-kutsut (luku 3).
- **Näkymä pysyy näkymänä.** Mallipohjaan ei voi kirjoittaa silmukkaa,
  joka hakee dataa, tai kymmenen rivin ehtolausetta. Logiikka on
  pakko siirtää komponentin koodiin, jossa sen voi nimetä ja testata.
- **Se on HTML:ää.** Attribuutit ovat `class` ja `for`, ja valmiin
  HTML-rakenteen voi liittää pohjaksi.
- **Kieli on opeteltava, ja se tarvitsee omat työkalunsa.** TypeScript
  ei ymmärrä mallipohjia, joten jokaisella kehyksellä on oma
  tarkistimensa ja editorilaajennuksensa:

```{.makefile tiedosto="esimerkit/Makefile" osa="tyypit"}
```

Kohteessa `tyypit` näkyy ero käytännössä: Reactille ja kehyksettömälle
toteutukselle riittää `tsc`, Vue tarvitsee `vue-tsc`:n, Svelte
`svelte-check`:n, ja Angularin mallipohjat tarkistaa sen oma kääntäjä
käännöksen yhteydessä.

## Erottelu tekniikan vai vastuun mukaan

Perinteinen web-kehityksen ohje oli pitää rakenne, tyyli ja toiminta
erillään: HTML, CSS ja JavaScript omissa tiedostoissaan. Angular jatkaa
tätä linjaa. Komponentissa on luokka ja erillinen mallipohja:

```{.typescript tiedosto="esimerkit/angular/src/app/sovellus.ts" osa="luokka"}
```

Luokka on näkymän **tietomalli**: se kertoo, mitä tilaa näkymällä on ja
mitä sillä voi tehdä, muttei mitään siitä, miltä se näyttää. Mallipohja
kertoo ulkoasun ja viittaa luokan kenttiin. Jako periytyy työpöytä- ja
palvelinsovellusten MVC- ja MVVM-arkkitehtuureista, joista AngularJS:n
tekijät tulivat, ja sillä on kolme käytännön perustelua. Luokan voi
testata ilman selainta. Mallipohjaa voi muokata koskematta logiikkaan,
ja suurissa organisaatioissa eri ihmiset tekevät näitä. Ja koska
mallipohja on dataa eikä koodia, kehys voi tarkistaa ja kääntää sen
etukäteen.

React perusteltiin vuonna 2013 päinvastoin: erottelu tekniikan mukaan
ei ole vastuiden erottelua. Näkymän merkintä ja sitä ohjaava logiikka
muuttuvat aina yhdessä. Kun listaan lisätään sarake, muuttuu sekä
mallipohja että koodi, joka tuottaa sarakkeen arvot. Ne ovat siis yksi
vastuu, jonka jakaminen kahteen tiedostoon ja kahteen kieleen vain
hajauttaa sen. Oikea raja kulkee **komponenttien** välissä: rivi,
lomake ja suodatin ovat eri vastuita, ja kukin niistä sisältää oman
rakenteensa ja logiikkansa.

Vue ja Svelte valitsivat välimuodon: yksi tiedosto komponenttia kohden,
mutta sen sisällä mallipohja, koodi ja tyylit ovat omissa lohkoissaan.

```{.html tiedosto="esimerkit/vue/src/Sovellus.vue" osa="skripti"}
```

Kiista on käytännössä ratkennut. Kaikissa neljässä kehyksessä
sovelluksen yksikkö on komponentti, ja Angularissakin pienen
komponentin mallipohja kirjoitetaan usein samaan tiedostoon. Jäljelle
jäi aidosti erilainen valinta vain siitä, onko näkymän kuvaus
ohjelmointikielen lauseke vai rajattu mallipohja, ja sen hyödyt ja
haitat on lueteltu yllä.

## Isäntäelementit ja tyhjätila

Kaksi pientä eroa tuli vastaan, kun toteutuksista tehtiin rakenteeltaan
samat.

**Angularin komponentilla on aina isäntäelementti.** Komponentti
`app-yhteenveto` näkyy DOM:ssa elementtinä `<app-yhteenveto>`, jonka
sisällä on mallipohjan sisältö. Muissa kehyksissä komponentti ei jätä
jälkeä: sen juurielementti on suoraan vanhemman lapsi. Useimmiten
ylimääräinen elementti ei haittaa, mutta `<ul>`:n lapsen on oltava
`<li>`. Siksi rivikomponentin valitsin on attribuutti, ja komponentti
liitetään olemassa olevaan `<li>`-elementtiin (luku 5).

**Tyhjätilan käsittely vaihtelee.** Rivinvaihto kahden elementin välissä
on HTML:ssä välilyönti. JSX poistaa sen, Vue ja Angular tiivistävät sen
omilla säännöillään ja Svelte omillaan. Ensimmäinen versio
testisarjasta vertasi rivin tekstisisältöä kokonaisena ja epäonnistui,
koska yhdessä toteutuksessa tehtävän nimen ja merkin välissä ei ollut
välilyöntiä. Testi korjattiin tarkistamaan elementit erikseen.

## Käytännössä

- **Pidä mallipohja tyhmänä kehyksestä riippumatta.** Ehto, joka ei
  mahdu yhdelle riville, kuuluu nimettyyn johdettuun arvoon
  (`nakyvat`, `valmiita`). Sääntö pätee myös JSX:ään, vaikka se sallisi
  enemmän.
- **Käytä kehyksen omaa tarkistinta CI:ssä.** Mallipohjan kirjoitusvirhe
  on muuten ajonaikainen virhe, joka näkyy vasta, kun näkymä avataan.
- **Älä taistele kehyksen tyyliä vastaan.** Angular-projektissa
  erilliset mallipohjat ja Reactissa JSX ovat se, mitä seuraava
  kehittäjä odottaa. Yhtenäisyys projektin sisällä on arvokkaampaa
  kuin oma mieltymys.
- **Älä vertaile tekstisisältöä elementtien yli testeissä.** Tyhjätila
  on kehyksen toteutusyksityiskohta. Testaa rooleja ja nimiä.

## Itsearviointi

- Osaat lukea saman näkymän neljällä kehyksellä ja löytää kustakin
  sidoksen, ehdon, listan ja avaimen.
- Osaat selittää, miksi JSX:n tarkistaa TypeScript mutta mallipohjat
  tarvitsevat kehyksen oman tarkistimen.
- Osaat kertoa, mitä kääntäjä voi tehdä rajatulle mallipohjalle mutta
  ei vapaalle koodille.
- Osaat esittää sekä Angularin että Reactin perustelun sille, miten
  näkymä ja logiikka jaetaan, ja sanoa, missä kohdin ne ovat samaa
  mieltä.
