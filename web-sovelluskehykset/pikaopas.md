---
title: Web-sovelluskehykset
subtitle: Pikaopas · React, Vue, Angular ja Svelte rinnakkain
---

# Kaksi kysymystä jokaisesta kehyksestä

| Kysymys | React | Vue | Angular | Svelte |
|-------|---------|---------|---------|---------|
| mistä kehys tietää, mikä muuttui | tilan asetus → koko komponentti uudelleen → vertailu | signaalit (`ref`) + käännetty vertailu | signaalit (ennen: `zone.js` ja tarkistus) | signaalit (riimut) + käännetyt DOM-kutsut |
| komponentin koodi ajetaan | joka päivityksellä | kerran | kerran | kerran |
| näkymän kuvaus | JSX: JavaScript-lauseke | mallipohja samassa tiedostossa | mallipohja, luokka erikseen | HTML:n laajennus |
| laajuus | näkymäkirjasto | ydin + viralliset lisäosat | kaikki samasta paikasta | kääntäjä + SvelteKit |

# Sama käsite, neljä nimeä

| Käsite | React | Vue | Angular | Svelte |
|--------|-------|--------|--------|--------|
| paikallinen tila | `useState` | `ref` | `signal` | `$state` |
| johdettu arvo | lauseke, `useMemo` | `computed` | `computed` | `$derived` |
| sivuvaikutus | `useEffect` | `watchEffect`, `watch` | `effect` | `$effect` |
| tieto alas | funktion parametri | `defineProps` | `input()` | `$props()` |
| tapahtuma ylös | takaisinkutsu | `defineEmits` | `output()` | takaisinkutsu |
| kaksisuuntainen sidos | ei; arvo + muutos | `v-model`, `defineModel` | `[(x)]`, `model()` | `bind:x`, `$bindable` |
| jaettu tila | konteksti | `provide` / `inject` | palvelu + `inject` | moduuli tai konteksti |
| viittaus elementtiin | `useRef` | `useTemplateRef` | `viewChild` | `bind:this` |
| välitetty sisältö | `children` | `<slot>` | `<ng-content>` | leike |

Nimet ovat loppuvuoden 2026 versioista (React 19, Vue 3.5, Angular 22,
Svelte 5). Rivit pysyvät, sarakkeiden sisältö vaihtuu.

# Mallipohjan rakenteet

| Asia | React | Vue | Angular | Svelte |
|------|-------|-----|---------|--------|
| teksti | `{x}` | `{{ x }}` | `{{ x() }}` | `{x}` |
| attribuutti | `disabled={x}` | `:disabled="x"` | `[disabled]="x()"` | `disabled={x}` |
| tapahtuma | `onClick={f}` | `@click="f"` | `(click)="f()"` | `onclick={f}` |
| ehto | `&&`, `? :` | `v-if`, `v-else` | `@if`, `@else` | `{#if}`, `{:else}` |
| lista | `xs.map(…)` | `v-for` | `@for` | `{#each}` |
| avain | `key={t.id}` | `:key="t.id"` | `track t.id` | `(t.id)` |

# Sama komponentti

```{.typescript tiedosto="esimerkit/react/src/Yhteenveto.tsx" osa="yhteenveto"}
```

```{.html tiedosto="esimerkit/vue/src/Yhteenveto.vue"}
```

```{.typescript tiedosto="esimerkit/angular/src/app/yhteenveto.ts" osa="yhteenveto"}
```

```{.html tiedosto="esimerkit/svelte/src/Yhteenveto.svelte"}
```

# Renderöintimallit

| Malli | Miten muutos löytyy | Hinta | Kehykset |
|----------|-----------|-----------|--------|
| virtuaalinen DOM | näkymä lasketaan uudelleen ja verrataan edelliseen | työ kasvaa näkymän koon mukaan | React, Preact |
| muutostentunnistus | sidokset käydään läpi jokaisen tapahtuman jälkeen | työ kasvaa sidosten määrän mukaan | AngularJS, Angular + `zone.js` |
| signaalit | arvo tietää lukijansa ja ilmoittaa niille | tila on käärittävä; riippuvuudet syntyvät ajon aikana | Vue, Angular, Svelte 5, Solid |
| kääntäjä | mallipohjasta tuotetaan täsmälliset päivitykset etukäteen | rakennusvaihe; tuotettu koodi kasvaa komponenttien mukana | Svelte, osin Vue ja Angular |

Mallit yhdistyvät: Vue on signaalit + virtuaalinen DOM + kääntäjä,
Svelte 5 signaalit + kääntäjä.

# Missä HTML syntyy

| Tekniikka | HTML syntyy | Sopii |
|----------|---------|-----------|
| selainrenderöinti (SPA) | selaimessa | kirjautumisen takana olevat sovellukset |
| palvelinrenderöinti + hydraatio | palvelimella, selain elävöittää | julkiset sivut, hakukoneet, hidas verkko |
| staattinen generointi | käännösvaiheessa | sisältö, joka muuttuu harvoin |
| saarekkeet, jatkettavuus | palvelimella, selaimeen vain osa | sisältösivut, joilla on vähän vuorovaikutusta |

Metakehykset: Next.js (React), Nuxt (Vue), SvelteKit (Svelte),
Angularin oma SSR.

# Valintakysymykset

1. Tarvitaanko sovelluskehystä, vai riittääkö palvelimen HTML ja vähän
   JavaScriptiä?
2. Mitä tiimi osaa ja ketä voidaan palkata?
3. Kuinka kauan sovellus elää, ja miten kehys on hoitanut aiemmat
   suuret muutoksensa?
4. Valmis kokonaisuus (Angular) vai osista koottu (React)?
5. Renderöidäänkö palvelimella? Silloin valitaan metakehys.
6. Mitä organisaatiossa jo käytetään?

Kehyksen vaihdon hintaa rajaa se, mikä ei tuo kehystä: säännöt,
tietotyypit, rajapinta-asiakas ja selaintestit.

# Komennot

| Komento | Tehtävä |
|---------|---------|
| `make` | asennus, tyypit, testit, käännökset ja selaintestit |
| `npx vite --config vue/vite.config.ts` | kehityspalvelin (react, vue, svelte, paljas) |
| `npx ng serve` | Angularin kehityspalvelin |
| `npx playwright test --project=svelte` | selaintestit yhdelle toteutukselle |
| `node --test yhteinen/logiikka.test.ts` | logiikan yksikkötestit |
| `node periaatteet/signaalit.ts` | renderöintimallin pienoistoteutus |
| `make tulokset` | mittaustulokset uudelleen |

# Dokumentaatio

| Kehys | Osoite |
|-------|--------|
| React | <https://react.dev> |
| Vue | <https://vuejs.org> |
| Angular | <https://angular.dev> |
| Svelte | <https://svelte.dev> |
