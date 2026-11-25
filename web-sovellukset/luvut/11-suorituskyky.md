# Suorituskyky

Hidas sovellus on käyttäjälle rikki samalla tavalla kuin virheellinen.
Selainsovelluksen suorituskyky ratkeaa kolmessa paikassa: kuinka paljon
koodia ladataan, kuinka monta verkkopyyntöä odotetaan peräkkäin ja
kuinka paljon työtä jokainen vuorovaikutus teettää. Ensin mitataan,
sitten korjataan.

## Mittarit

Googlen *Core Web Vitals* ovat yleisin mittaristo:

| Mittari | Mittaa | Hyvä |
|---------|--------|------|
| LCP (*Largest Contentful Paint*) | milloin pääsisältö näkyy | enintään 2,5 s |
| INP (*Interaction to Next Paint*) | kuinka nopeasti vuorovaikutus näkyy | enintään 200 ms |
| CLS (*Cumulative Layout Shift*) | kuinka paljon sisältö hyppii | enintään 0,1 |

Kehittäjän kone ja verkko ovat moninkertaisesti nopeampia kuin
käyttäjän puhelin. Mittaa siksi hidastetulla prosessorilla ja verkolla
(selaimen kehitystyökalut, Lighthouse) ja kerää todelliset arvot
käyttäjiltä (`web-vitals`-kirjasto). Reactin kehitystyökalujen
Profiler näyttää, mitkä komponentit renderöityvät ja kuinka kauan.

## Paketin koko ja koodin pilkkominen

Kaikki JavaScript on ladattava, jäsennettävä ja suoritettava ennen kuin
SPA näyttää mitään. Esimerkkisovelluksen pääpaketti on noin 230 kt
(tiivistettynä 72 kt), josta valtaosa on Reactia. Harvoin käytetty
raporttinäkymä ladataan omana tiedostonaan vasta, kun käyttäjä avaa sen
(`lazy` ja `Suspense` luvun 8 sovelluksessa). Vite tekee jokaisesta
dynaamisesta `import()`-kutsusta oman tiedostonsa.

Pilkkominen kannattaa reittien ja raskaiden osien (kaaviokirjasto,
editori) rajoilta. Liian pieni pilkkominen tuottaa vesiputouksen, jossa
tiedosto lataa tiedoston, joka lataa tiedoston. `vite build` raportoi
tiedostojen koot; `rollup-plugin-visualizer` näyttää, mistä ne
koostuvat.

## Verkon vesiputoukset

Peräkkäiset `await`-kutsut odottavat toisiaan, vaikka pyynnöt olisivat
riippumattomia:

```{.typescript tiedosto="esimerkit/src/11-suorituskyky/vesiputous.ts" osa="vesiputous"}
```

![Testin kolme 100 millisekunnin pyyntöä peräkkäin ja
rinnakkain.](kuvat/11-vesiputous.png){width=100%}

Testi mittaa näennäisaikaa: kolme 100 millisekunnin pyyntöä kestää
peräkkäin 300 ja rinnakkain 100 millisekuntia. Sama ilmiö syntyy
komponenttipuussa, kun lapsi aloittaa hakunsa vasta, kun vanhemman haku
on valmis ja lapsi on renderöity. Siksi datan haku kannattaa aloittaa
mahdollisimman aikaisin, esimerkiksi reitin vaihtuessa ennen
renderöintiä (*render-as-you-fetch*), kuten reitittimet ja
SSR-kehykset tekevät.

## Turhat renderöinnit

Vanhemman renderöinti renderöi lapset, vaikka niiden propsit eivät
muuttuneet. Yleensä tämä on nopeaa, mutta raskas lista hidastaa
jokaista näppäilyä. `memo` ohittaa renderöinnin, jos propsit ovat samat.
Vertailu on viitevertailu, joten joka renderöinnissä luotu funktio
rikkoo sen:

```{.typescript tiedosto="esimerkit/src/11-suorituskyky/Renderoinnit.tsx" osa="memo"}
```

```{.typescript tiedosto="esimerkit/src/11-suorituskyky/Renderoinnit.test.tsx" osa="testi"}
```

`memo` ilman vakaita propseja on pelkkä lisäkustannus: vertailu tehdään,
ja renderöinti tehdään silti. Ensisijainen korjaus on usein rakenteellinen:
siirrä usein muuttuva tila alemmas (tässä muistiinpanokenttä omaan
komponenttiinsa), jolloin lista ei renderöidy lainkaan. React
Compiler lisää muistamisen automaattisesti käännösvaiheessa, mikä
vähentää käsin kirjoitettujen `memo`- ja `useCallback`-kutsujen tarvetta.

Pitkät listat (tuhansia rivejä) piirretään *virtualisoituna*: DOM:iin
luodaan vain näkyvät rivit (TanStack Virtual). Raskas laskenta, joka
ei liity näkymään, siirretään Web Workeriin.

## Käytännössä

- **Mittaa ensin, oikealla laitteella.** Optimointi ilman mittausta
  korjaa väärän asian.
- **Koodia vähemmän, ei nopeammin.** Jokainen riippuvuus maksaa
  latauksessa. Tarkista koko ennen lisäämistä (bundlephobia), ja pilko
  reittien rajoilta.
- **Rinnakkaiset haut ja aikainen aloitus.** `Promise.all`
  riippumattomille pyynnöille; haku reitin vaihtuessa, ei lapsen
  efektissä.
- **Tilan sijainti ennen `memo`a.** Usein muuttuva tila alas;
  `memo` ja `useCallback` vasta, kun Profiler näyttää ongelman.
- **CLS:n välttäminen:** kuville leveys ja korkeus, latausnäkymät
  oikean kokoisina, ei sisältöä olemassa olevan yläpuolelle.

## Itsearviointi

- Osaat nimetä Core Web Vitals -mittarit ja mitata ne realistisissa
  olosuhteissa.
- Osaat pilkkoa koodin `lazy`- ja `Suspense`-rakenteilla ja tunnistaa
  verkon vesiputouksen.
- Osaat selittää, milloin `memo` auttaa ja miksi uusi funktio-propsi
  rikkoo sen.
- Osaat nopeuttaa pitkää listaa virtualisoinnilla ja siirtää raskaan
  laskennan pois pääsäikeestä.
