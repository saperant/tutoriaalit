---
title: Rinnakkaisohjelmointi
subtitle: Pikaopas · säikeet, muistimalli, lukot, lukottomat rakenteet ja ThreadSanitizer
lang: fi
---

# Säikeet ja tehtävät

| Väline | Huomio |
|----------------------|---------------------------|
| `std::jthread t{f, args...}` | Kopioi argumentit; `std::ref(x)` viittaukselle; odottaa ja pysäyttää hajottimessa |
| `std::stop_token` | `f(std::stop_token t, ...)`; `t.stop_requested()` |
| `std::stop_callback cb{t, g}` | `g` ajetaan `request_stop`issa; määrittele säikeen *jälkeen* vain, jos pyydät pysäytyksen itse |
| `cv_any.wait(lukko, t, ehto)` | Herää myös pysäytykseen; palauttaa `ehto()` |
| `std::async(std::launch::async, f)` | Tallenna future: muuten hajotin odottaa heti |
| `std::promise` / `std::future` | `set_value`, `set_exception`; `get` kerran, `share()` monelle |
| `std::packaged_task<R()>` | Funktio, jonka tulos ja poikkeus menevät futureen |
| `thread_local` | Oma kopio jokaiselle säikeelle; poolissa säilyy tehtävästä toiseen |

- **Elinajat:** säikeet määritellään viimeisinä; sieppaukset nimetään.
- **Poikkeus säikeestä** kaataa ohjelman, ellei sitä välitetä
  (`std::exception_ptr`, `promise`).
- **Pooli:** lukko + ehtomuuttuja + `std::move_only_function`-jono;
  tehtävä suoritetaan lukon ulkopuolella; älä odota saman poolin tulosta.

# Muistimalli

- **Datakilpailu:** sama paikka, ainakin yksi kirjoitus, ei
  tapahtumisjärjestystä, ainakin yksi ei-atominen. Määrittelemätöntä.
- **Tapahtumisjärjestys** = peräkkäisyys + synkronointi (release →
  acquire *samassa muuttujassa*, unlock → lock, luonti, `join`).
- **SC for DRF:** ilman kilpailuja ja `seq_cst`-järjestyksellä ohjelma
  käyttäytyy kuin lomitettu yksisäikeinen.

| Järjestys | Käyttö |
|-----------------|--------------------------------|
| `relaxed` | Laskurit, tilastot |
| `release` (kirjoitus) | Julkaisu, lukon vapautus |
| `acquire` (luku) | Julkaistun datan luku, lukon otto |
| `acq_rel` | Luku–kirjoitus-operaatio kumpaankin suuntaan |
| `seq_cst` | Oletus; tarvitaan "kirjoita, sitten lue toinen" -tilanteissa |

| Litmus | `relaxed` | rel/acq | `seq_cst` | x86 | ARM |
|--------|--------|--------|--------|---------|---------|
| SB (0,0) | sallittu | sallittu | kielletty | esiintyy | esiintyy |
| MP (1,0) | sallittu | kielletty | kielletty | ei esiinny | esiintyy |

# Atomiset operaatiot

| Operaatio | Huomio |
|----------------------|---------------------------|
| `load`, `store`, `exchange` | `exchange` palauttaa vanhan |
| `fetch_add`, `fetch_or`, ... | Palauttavat vanhan; `++` palauttaa uuden |
| `compare_exchange_weak(v, u)` | Silmukassa; epäonnistuessa `v` = nykyinen |
| `compare_exchange_strong` | Kertayritykseen |
| `wait(vanha)`, `notify_one/all` | Nukkuu futexissa, kunnes arvo muuttuu |
| `is_always_lock_free` | Tarkista käännösaikana; > 8 tavua x86:lla usein piilolukko |
| `std::atomic_ref<T>{x}` | Tavallinen olio atomisena; kaikki samanaikaiset käyttäjät sen kautta |

```{.cpp tiedosto="esimerkit/05-atomiset.cpp" osa="maksimi"}
```

# Lukot ja odotus

| Tarve | Väline |
|-------------------------|-------------------------|
| Yksi tai monta lukkoa, ei lukkiutumista | `std::scoped_lock l{a, b}` |
| Ehtomuuttujan kanssa | `std::unique_lock` |
| Monta lukijaa, yksi kirjoittaja | `std::shared_mutex` + `shared_lock` / `unique_lock` |
| Odota ehtoa | `cv.wait(lukko, ehto)`; ilmoitus lukon jälkeen |
| Lähtöportti, odota N | `std::latch` |
| Toistuvat vaiheet | `std::barrier{n, valmis}`; `arrive_and_wait` |
| Enintään N käyttäjää | `std::counting_semaphore<N>` |
| Alusta kerran | Paikallinen `static`, `std::call_once` |

- **Ongelmat:** lukkiutuminen, elolukko, jonoutuminen (I/O lukon alla),
  prioriteetin inversio (`PTHREAD_PRIO_INHERIT`).
- **Karkeus:** yksi lukko → raidoitus → hienojakoinen; mittaa välissä.

# Lukottomat rakenteet

| Rakenne | Ydin | Takaisinotto |
|------------|--------------------|-----------------|
| SPSC-rengas | Kaksi julkaisuparia, ei CAS:ia | Ei tarvita |
| Treiberin pino | CAS päähän | Vaaraosoittimet tai epookit |
| MPMC (Vjukov) | Paikan järjestysnumero + CAS indekseihin | Ei tarvita (kiinteä taulukko) |
| Kopioi ja vaihda | `atomic<shared_ptr<const T>>` + CAS | Viittauslaskenta |

- **ABA:** CAS ei huomaa poistettua ja palautettua solmua. Ratkaisut:
  versiolaskuri, LL/SC, turvallinen takaisinotto.
- **Vaaraosoitin:** ilmoita, lue pää uudelleen (`seq_cst`), CAS, poista
  ilmoitus, siirrä solmu listalle; vapauta erissä solmut, joihin kukaan
  ei osoita.
- **Edistymistakuut:** estävä < esteetön < lukoton < odotukseton.

# Rinnakkaiset algoritmit

- `std::reduce(std::execution::par, ...)`: operaation oltava liitännäinen
  ja vaihdannainen. libstdc++ tarvitsee TBB:n (`-ltbb`), muuten sarjallinen.
- `par_unseq`: ei lukkoja eikä varauksia funktiossa.
- **Reduktio:** paikallinen osasumma, yksi kirjoitus, yhdistys
  indeksijärjestyksessä (toistettava liukulukutulos).
- **Prefiksisumma:** lohkojen scan → lohkosummien eksklusiivinen scan →
  siirtymän lisäys.
- **Työnjako:** staattinen (deterministinen), syklinen (säännöllinen hinta),
  dynaaminen erälaskuri (tuntematon hinta), työnvarastaminen (skaalautuu).
- **Amdahl:** $S = 1/(s + (1-s)/p) \le 1/s$; **Gustafson:**
  $S = s + (1-s)p$.
- **Väärä jakaminen:** kuumat säiekohtaiset muuttujat
  `alignas(std::hardware_destructive_interference_size)`; rajapinnoissa
  kiinteä `alignas(64)`.

# ThreadSanitizer

```text
g++-14 -std=c++23 -g -O1 -fsanitize=thread ohjelma.cpp
TSAN_OPTIONS="halt_on_error=1 second_deadlock_stack=1" ./a.out
```

| Raportti | Merkitys |
|-----------------|--------------------------------|
| `data race` | Kaksi viittausta ilman tapahtumisjärjestystä; katso `#0`-kehykset ja `Location` |
| `lock-order-inversion` | Sykli lukkojen järjestyksessä: voi lukkiutua |
| `heap-use-after-free` (ASan) | Takaisinottovirhe |

- **Ei löydä:** atomisuusrikot (tarkista ja toimi), ajamaton koodi, liian
  heikot kilpailuttomat järjestykset, jumittuneet odotukset,
  instrumentoimaton koodi, aidat.
- **Täydennä:** stressitesti (yhteinen lähtö, monta lyhyttä kierrosta,
  satunnainen `yield`, invariantit), `rr --chaos`, mallintarkastimet
  (GenMC, CDSChecker), `-Wthread-safety`, AArch64-kone CI:ssä.
- **Pienennä löydetty virhe** deterministiseksi testiksi esteillä.
