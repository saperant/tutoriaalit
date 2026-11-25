# Reititys ja palvelinrenderöinti

Tehtävälista on yksi näkymä, joka rakentuu kokonaan selaimessa.
Oikeissa sovelluksissa näkymiä on monta, ja usein ensimmäinen niistä
halutaan näkyviin ennen kuin JavaScript on ladattu. Näihin kahteen
tarpeeseen, reititykseen ja palvelinrenderöintiin, kehykset tarjoavat
omat ratkaisunsa tai jättävät ne **metakehyksille**. Tämä luku käy
käsitteet läpi ilman, että sovellusta laajennetaan: rajapinnat
muuttuvat tässä kerroksessa nopeimmin, mutta käsitteet ovat pysyneet.

Sovellusarkkitehtuurien perusjako (monisivuinen, yksisivuinen,
palvelinrenderöity, staattinen) on esitelty taidossa *Web-sovellukset*.

## Reititys

Yksisivuisessa sovelluksessa osoiterivi on tilaa: se kertoo, mikä
näkymä on esillä. **Reititin** on komponentti tai kirjasto, joka pitää
osoitteen ja näkymän yhdessä. Se kuuntelee osoitteen muutoksia,
valitsee osoitetta vastaavan komponentin ja tarjoaa linkit, jotka
vaihtavat näkymää lataamatta sivua.

| Kehys | Reititin | Reittien kuvaus |
|-------|----------|-----------------|
| React | erillinen kirjasto (React Router, TanStack Router) tai metakehys | koodissa tai tiedostorakenteesta |
| Vue | Vue Router, kehyksen tekijöiltä | koodissa; Nuxtissa tiedostorakenteesta |
| Angular | kehyksen oma reititin | koodissa |
| Svelte | SvelteKit | tiedostorakenteesta |

Erosta näkyy luvun 1 jako kirjastoon ja kehykseen. Angularin reititin
tulee kehyksen mukana ja on jokaisessa Angular-sovelluksessa sama.
Reactissa reititin on valinta, ja valintoja on useita.

Kaikissa reitittimissä ovat samat käsitteet: reitin parametrit
(`/tehtavat/:id`), sisäkkäiset reitit, joissa kehysnäkymä pysyy ja
sisältö vaihtuu, datan lataus ennen näkymän näyttämistä sekä koodin
pilkkominen niin, että reitin koodi ladataan vasta, kun reitille
tullaan.

## Sama näkymä palvelimella

"Näkymä on tilan funktio" pätee myös ilman selainta. Sama funktio, joka
selaimessa tuottaa DOM-päivityksiä, voi palvelimella tuottaa
HTML-merkkijonon. Alla sama lista renderöidään Nodessa Reactilla ja
Vuella. Näkymät on kirjoitettu ilman JSX:ää ja mallipohjaa, suoraan
niillä kutsuilla, joiksi ne käännetään:

```{.typescript tiedosto="esimerkit/periaatteet/palvelin.ts" osa="nakymat"}
```

```{.typescript tiedosto="esimerkit/periaatteet/palvelin.ts" osa="palvelin"}
```

```{.tuloste tiedosto="esimerkit/periaatteet/palvelin.odotettu"}
```

Kaksi eri kehystä tuottaa samasta tilasta saman HTML:n. Selain voi
näyttää sen heti, ennen kuin yhtään JavaScript-tiedostoa on ladattu.
Tämä on **palvelinrenderöinti** (SSR).

## Hydraatio

Palvelimen tuottama HTML on kuollutta: siinä ei ole
tapahtumankäsittelijöitä eikä tilaa. Jotta sivusta tulee sovellus,
selaimessa ajetaan **hydraatio**: kehys lataa komponenttien koodin,
ajaa näkymäfunktiot samalla tilalla kuin palvelin, olettaa tuloksen
vastaavan valmista HTML:ää ja liittää käsittelijät olemassa oleviin
elementteihin luomatta niitä uudelleen.

```{.dot otsikko="Palvelinrenderöinti ja hydraatio: sisältö näkyy aikaisin, mutta sivu vastaa käyttäjälle vasta hydraation jälkeen"}
digraph {
  rankdir=LR; ranksep=0.3;
  a [label="palvelin ajaa\nnäkymän:\nHTML + tila"];
  b [label="selain näyttää\nHTML:n: sivu näkyy\nmutta ei toimi"];
  c [label="JavaScript\nladataan"];
  d [label="hydraatio:\nnäkymä ajetaan\nuudelleen"];
  e [label="sivu vastaa\nkäyttäjälle"];
  a -> b -> c -> d -> e;
}
```

Hydraatiolla on kolme hintaa, jotka selittävät lähes kaiken, mitä
kehykset ovat tällä alueella viime vuosina tehneet:

- **Työ tehdään kahdesti.** Palvelin renderöi näkymän, ja selain
  renderöi sen uudelleen vain löytääkseen, mihin käsittelijät
  kuuluvat. Selaimeen ladataan koko sovelluksen koodi, myös niille
  osille, jotka eivät koskaan muutu.
- **Palvelimen ja selaimen on oltava samaa mieltä.** Jos näkymä riippuu
  jostain, mikä on eri paikoissa eri (kellonaika, satunnaisluku,
  selaimen muisti), hydraatio löytää ristiriidan. Tehtävälistan tila
  ladataan selaimen muistista, joten se ei sellaisenaan sovi
  palvelimella renderöitäväksi.
- **Näkymisen ja toimimisen välissä on aukko.** Painike näkyy, mutta
  sen painaminen ei tee mitään ennen kuin hydraatio on valmis.

Kehysten vastaukset ovat muunnelmia samasta ajatuksesta: lähetetään
selaimeen vähemmän koodia ja hydratoidaan vähemmän kerralla.

| Tekniikka | Ajatus | Esimerkkejä |
|-------|----------------|-------|
| suoratoisto | HTML lähetetään osissa sitä mukaa kuin data valmistuu | useimmat metakehykset |
| osittainen hydraatio | vain vuorovaikutteiset osat hydratoidaan | Astron saarekkeet |
| palvelinkomponentit | osa komponenteista ajetaan vain palvelimella, eikä niiden koodia lähetetä | React, Next.js |
| laiska hydraatio | komponentti hydratoidaan vasta, kun se tulee näkyviin tai sitä käytetään | Angular, Vue, Nuxt |
| jatkettavuus | tila ja käsittelijät sarjallistetaan HTML:ään, eikä näkymää ajeta uudelleen | Qwik |

Nimet ja rajapinnat ovat tämän hetken yksityiskohtia. Pysyvä asia on
kolmen hinnan luettelo: jokaisen uuden tekniikan kohdalla voi kysyä,
mitä niistä se pienentää ja mitä se vaatii vastineeksi.

## Metakehykset

Palvelinrenderöinti tarvitsee palvelimen, reitityksen molemmissa
päissä, datan latauksen ja rakennusjärjestelmän, joka tuottaa koodista
kaksi versiota. Tämä kokonaisuus on **metakehys**: Reactille Next.js ja
React Router, Vuelle Nuxt, Sveltelle SvelteKit. Angularissa
palvelinrenderöinti on kehyksen oma osa.

Metakehys on suurempi sitoumus kuin käyttöliittymäkirjasto. Se
määrää tiedostorakenteen, datan latauksen tavan ja usein myös sen,
missä sovellus ajetaan. Käyttöliittymäkomponentit siirtyvät
metakehyksestä toiseen kohtuullisella työllä, reitit ja datan lataus
eivät.

## Käytännössä

- **Valitse renderöintitapa näkymän, ei sovelluksen mukaan.** Julkinen
  etusivu ja tuotesivu hyötyvät palvelinrenderöinnistä (nopea
  ensimmäinen näkymä, hakukoneet). Kirjautumisen takana oleva
  työkalunäkymä ei, ja se on yksinkertaisempi selaimessa
  renderöitynä. Metakehykset sallivat valinnan reittikohtaisesti.
- **Älä ota palvelinrenderöintiä oletuksena.** Se tuo palvelimen,
  jota pitää ajaa ja valvoa, ja luokan virheitä, joita selaimessa
  renderöidyssä sovelluksessa ei ole. Staattinen sivusto tai
  yksisivuinen sovellus staattisilta palvelimilta on halvempi ajaa ja
  helpompi ymmärtää.
- **Pidä näkymät puhtaina, niin ne toimivat palvelimellakin.**
  Komponentti, joka lukee `window`-oliota tai selaimen muistia
  renderöinnin aikana, ei toimi palvelimella. Selaimesta riippuva
  koodi kuuluu efekteihin, jotka ajetaan vain selaimessa.
- **Moduulitason tila on palvelimella yhteinen kaikille käyttäjille**
  (luku 7). Tämä on palvelinrenderöinnin tavallisin tietovuoto.
- **Linkit ovat linkkejä.** Reititin ei saa rikkoa selaimen omaa
  toimintaa: osoitteen kopiointia, paluupainiketta ja linkin avaamista
  uuteen välilehteen.

## Itsearviointi

- Osaat selittää, mitä reititin tekee ja mitkä käsitteet ovat
  yhteisiä kaikille reitittimille.
- Osaat kuvata palvelinrenderöinnin ja hydraation vaiheet ja sen, miksi
  sivu voi näkyä ennen kuin se toimii.
- Osaat nimetä hydraation kolme hintaa ja arvioida uutta tekniikkaa
  niiden avulla.
- Osaat perustella, milloin näkymä kannattaa renderöidä palvelimella
  ja milloin ei.
- Osaat kertoa, mitä metakehys tuo käyttöliittymäkirjaston päälle ja
  miksi se on suurempi sitoumus.
