# React-komponentit

Luvussa 3 nähtiin kaksi tapaa pitää näkymä tilan tasalla: sovitus ja
signaalit. React valitsee sovituksen: komponentit kuvaavat näkymän, ja
React vertaa kuvausta edelliseen ja päivittää DOM:n. Tästä luvusta
eteenpäin sovellus rakennetaan Reactilla.

React-komponentti on funktio, joka saa syötteenä *propsit* ja palauttaa
kuvauksen näkymästä. JSX on tälle kuvaukselle kirjoitettu syntaksi:
`<h3>{tila.nimi}</h3>` kääntyy funktiokutsuksi, joka luo olion
`{ type: "h3", props: { children: tila.nimi } }`. Lausekkeet
aaltosulkeissa ovat tavallista TypeScriptiä, ja tekstiksi päätyvä arvo
koodataan aina turvallisesti: merkkijono `"<img …>"` näkyy tekstinä.

## Komponentit ja propsit

```{.typescript tiedosto="esimerkit/src/04-react/TilaKortti.tsx" osa="kortti"}
```

Propsien tyyppi on komponentin rajapinta, ja TypeScript tarkistaa
jokaisen käyttökohdan. Valinnainen `onVaraa` tekee kortista
uudelleenkäytettävän: ilman sitä kortti on pelkkä esitys. Ehdollinen
osa kirjoitetaan `&&`-lausekkeena tai ehtolausekkeena. Varo
`&&`-lauseketta luvulla: `{lkm && <p>…</p>}` näyttää nollan, koska
React piirtää luvun `0`. Ehto kirjoitetaan siksi totuusarvoksi
(`lkm > 0 &&`).

Komponentti on **puhdas**: samoilla propseilla ja tilalla se palauttaa
saman kuvauksen eikä muuta mitään ulkopuolista. React voi siksi ajaa
sen milloin tahansa ja kuinka monta kertaa tahansa. Kehitystilan
`StrictMode` ajaa komponentit tarkoituksella kahdesti paljastaakseen
epäpuhtaat komponentit.

## Listat ja avaimet

```{.typescript tiedosto="esimerkit/src/04-react/TilaLista.tsx" osa="lista"}
```

Avain (`key`) kertoo Reactille, mikä listan alkio on mikä, kun lista
muuttuu. Sen perusteella React päättää, säilyttääkö se olemassa olevan
komponentin ja sen tilan. Avaimen on oltava vakaa ja yksilöivä tieto
datasta, yleensä tunniste. Taulukon indeksi avaimena on yleinen virhe:

```{.typescript tiedosto="esimerkit/src/04-react/Avaimet.tsx" osa="avaimet"}
```

```{.typescript tiedosto="esimerkit/src/04-react/Avaimet.test.tsx" osa="testi"}
```

Kun ensimmäinen rivi poistetaan, Einon rivi saa indeksin 0. React
näkee avaimen 0 yhä listassa ja säilyttää sen komponentin, jossa on
Ainon kirjoittama teksti. Indeksi kelpaa avaimeksi vain listaan, jonka
järjestys ei koskaan muutu eikä alkioilla ole tilaa.

## Tila ja tilan nostaminen

`useState` antaa komponentille muistin renderöintien välillä. Kutsu
palauttaa nykyisen arvon ja asetusfunktion. Asetus ei muuta arvoa
heti vaan pyytää uuden renderöinnin, jossa komponentti saa uuden arvon.
Saman käsittelijän useat asetukset niputetaan yhdeksi renderöinniksi.

Kun kaksi komponenttia tarvitsee saman tiedon, tila **nostetaan**
lähimpään yhteiseen esivanhempaan, ja se välittää arvon alas propseina
ja muutokset ylös takaisinkutsuina. Tämä on **yksisuuntainen
datavirta**: data kulkee alas, tapahtumat ylös.

```{.typescript tiedosto="esimerkit/src/04-react/TilaHaku.tsx" osa="haku"}
```

```{.dot otsikko="Haun komponenttipuu: data kulkee propseina alas ja tapahtumat takaisinkutsuina ylös. Tila on lähimmässä yhteisessä esivanhemmassa." leveys="50%"}
digraph {
  rankdir=TB; ranksep=0.5;
  H [label="TilaHaku\ntila: haku, vahintaan\njohdettu: osumat",
     style="filled,bold", fillcolor="#E6EDF7"];
  K [label="hakukentät\n(<input>)"];
  L [label="TilaLista"];
  C [label="TilaKortti × n"];
  H -> K [label="value ↓\nonChange ↑"];
  H -> L [label="tilat = osumat ↓\nonVaraa ↑"];
  L -> C [label="tila ↓\nonVaraa ↑"];
}
```

![Sama komponenttipuu selaimessa, kun hakukenttään on kirjoitettu
"ki": osumia on yksi neljästä.](kuvat/04-haku.png){width=70%}

`TilaHaku` on *konttikomponentti* (*container component*): se omistaa
tilan ja päättää, mitä näytetään. `TilaLista` ja `TilaKortti` ovat
*esityskomponentteja*. Jako
tekee esityskomponenteista helppoja testata ja käyttää uudelleen.
Suodatettu lista lasketaan renderöinnissä, kuten luvun 3 periaate
sanoo. Kenttien arvot ovat Reactin tilassa (*kontrolloidut kentät*), ja
`aria-live`-alue kertoo ruudunlukijalle osumien määrän.

Testi käyttää Testing Libraryä, joka hakee elementit niin kuin käyttäjä
ne löytää: roolin ja saavutettavan nimen perusteella. Testi on samalla
saavutettavuustesti, sillä nimetön kenttä ei löytyisi. Toisin kuin
luvun 3 uudelleenrakennus, React säilyttää kentän ja sen fokuksen:

```{.typescript tiedosto="esimerkit/src/04-react/TilaHaku.test.tsx" osa="testi"}
```

## Renderöinnin malli

React päivittää näkymän kahdessa vaiheessa. **Renderöinnissä** se
kutsuu komponentteja, joiden tila tai propsit muuttuivat, ja niiden
lapsia, ja vertaa tulosta edelliseen. **Kiinnityksessä** (*commit*) se
tekee erot DOM:iin ja ajaa efektit (luku 6). Komponentin renderöinti ei
siis tarkoita DOM-muutosta. Oletuksena vanhemman renderöinti renderöi
kaikki lapset; luvussa 11 nähdään, milloin tämä on hidasta ja miten
sen voi estää.

```{.dot otsikko="Päivityksen kierros Reactissa. Renderöinti on puhdasta laskentaa, ja DOM muuttuu vasta kiinnityksessä."}
digraph {
  rankdir=LR; ranksep=0.3; nodesep=0.3;
  t [label="tapahtuma:\nsetHaku(\"ki\")", shape=ellipse];
  r [label="renderöinti:\nkomponentit ajetaan,\nuusi kuvaus"];
  v [label="sovitus:\nvertailu\nedelliseen"];
  c [label="kiinnitys:\nerot DOM:iin", style="filled,bold",
     fillcolor="#E6EDF7"];
  e [label="efektit\n(luku 6)"];
  n [label="selain\npiirtää", shape=ellipse];
  t -> r -> v -> c -> e;
  c -> n;
}
```

React ei ole ainoa tapa. **Vue** kirjoittaa näkymän HTML-pohjana
(`<li v-for="t in tilat" :key="t.id">{{ t.nimi }}</li>`), ja sen tila
on signaaleja (`ref`, `computed`), joten komponentti ajetaan kerran ja
vain muuttuneet kohdat päivittyvät. Käsitteet ovat samat: komponentit,
propsit alas, tapahtumat ylös, avaimet listoissa, johdetut arvot.
Sama sovellus Reactilla, Vuella, Angularilla ja Sveltellä on taidossa
*Web-sovelluskehykset ja niiden periaatteet*.

## Käytännössä

- **Pienet komponentit, selvät rajapinnat.** Komponentti tekee yhden
  asian, ja sen propsit on tyypitetty. Kun propseja on yli kymmenen tai
  komponentti on satoja rivejä, se jaetaan.
- **Kontti- ja esityskomponentit.** Data, tila ja sivuvaikutukset
  konttiin; esityskomponentti saa kaiken propseina. Malli ei ole
  dogmi, mutta se pitää suurimman osan komponenteista puhtaina.
- **Johda, älä synkronoi.** Jos arvon voi laskea propseista tai
  tilasta, se lasketaan renderöinnissä. Kaksi tilaa, jotka on pidettävä
  samana, on yksi tila liikaa.
- **Avaimet datasta.** `key={rivi.id}`. Ilman vakaata tunnistetta data
  saa tunnisteen, kun se luodaan (`crypto.randomUUID()`), ei
  renderöinnissä.
- **Tilan sijainti.** Tila mahdollisimman alas puuhun, mutta niin
  ylös, että kaikki sitä tarvitsevat näkevät sen. Liian ylhäällä oleva
  tila renderöi turhaan suuren osan sovelluksesta.
- **Testaa käyttäjän näkökulmasta.** `getByRole` ja `getByLabelText`
  ennen `getByTestId`-hakua. Testi ei saa riippua komponentin
  sisäisestä tilasta tai rakenteesta.

## Itsearviointi

- Osaat kirjoittaa tyypitetyn komponentin, ehdollisen sisällön ja
  listan oikein avaimin.
- Osaat selittää, miksi indeksiavain siirtää tilan väärälle riville.
- Osaat nostaa tilan yhteiseen esivanhempaan ja erottaa kontti- ja
  esityskomponentit.
- Osaat kuvata Reactin renderöinti- ja kiinnitysvaiheen ja verrata
  mallia Vuen signaaleihin.
- Osaat testata komponentin Testing Libraryllä roolien ja nimien
  perusteella.
