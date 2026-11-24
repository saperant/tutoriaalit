---
title: Korkean tason mallinnus
subtitle: Pikaopas · SystemC 2.3, TLM-2.0 ja virtuaaliprototyypit
---

# Kääntäminen

| Tarve | Valitsin tai komento |
|-------|----------------------|
| kääntäjä, standardi | `g++ -std=c++17` (sama kuin kirjastolla) |
| kirjasto | `pkg-config --cflags --libs systemc` |
| kiintopistetyypit | `-DSC_INCLUDE_FX` |
| ei käynnistysilmoitusta | `SC_COPYRIGHT_MESSAGE=DISABLE` |
| RTL SystemC-moduuliksi | `verilator --sc --exe --build` |
| aaltomuodot | `sc_create_vcd_trace_file`, `sc_trace` |

# Moduuli

```{.cpp tiedosto="esimerkit/01-laskuri/laskuri.hpp" osa="moduuli"}
```

| Rakenne | Merkitys |
|---------|----------|
| `SC_MODULE(M)` | `struct M : sc_module` |
| `SC_CTOR(M)` | rakennin, joka ottaa nimen |
| `sc_in<T>`, `sc_out<T>`, `sc_inout<T>` | signaaliportit |
| `sc_port<IF>`, `sc_export<IF>` | rajapintaportti, julkaistu rajapinta |
| `sensitive << s` | herkkyys signaalin muutokselle |
| `sensitive << clk.pos()` | nousevalle reunalle |
| `dont_initialize()` | ei alustusajoa |
| `start_of_simulation()` | ajetaan ennen ensimmäistä prosessia |

# Prosessit ja odotus

| Tyyppi | Odotus |
|--------|--------|
| `SC_METHOD` | ei odota; `next_trigger(...)` |
| `SC_THREAD` | `wait(...)` |
| `SC_CTHREAD` | `wait()` = seuraava kellonreuna |

| Kutsu | Odottaa |
|-------|---------|
| `wait()` | staattista herkkyyttä |
| `wait(e)` | tapahtumaa |
| `wait(t)` | aikaa |
| `wait(t, e)` | tapahtumaa aikarajalla; `e.triggered()` |
| `wait(SC_ZERO_TIME)` | yhtä delta-sykliä |

| Ilmoitus | Odottaja herää |
|----------|----------------|
| `e.notify()` | samassa arviointivaiheessa |
| `e.notify(SC_ZERO_TIME)` | seuraavassa delta-syklissä |
| `e.notify(t)` | ajan `t` kuluttua |

Tapahtumalla ei ole muistia: tila ensin, sitten odotus.

# Simulaatioydin

| Vaihe | Tapahtuu |
|-------|----------|
| elaborointi | moduulit, kanavat ja kytkennät (ennen `sc_start`ia) |
| alustus | prosessit ajetaan kerran (paitsi `dont_initialize`) |
| arviointi | ajettavat prosessit; kirjoitukset odottavat |
| päivitys | kanavat (`update()`); muutostapahtumat |
| delta | uusi kierros samalla hetkellä |
| ajan siirto | seuraavaan ajastettuun ilmoitukseen |

| Funktio | Merkitys |
|---------|----------|
| `sc_start()`, `sc_start(t)` | simuloi loppuun tai ajan `t` |
| `sc_stop()` | pysäyttää |
| `sc_time_stamp()` | nykyinen aika |
| `sc_delta_count()` | delta-syklien laskuri |
| `sc_set_time_resolution(1, SC_PS)` | ennen ensimmäistä aikaa |

# Kanavat

| Kanava | Käyttö |
|--------|--------|
| `sc_signal<T>` | yksi kirjoittaja, tapahtuma muutoksesta |
| `sc_buffer<T>` | tapahtuma jokaisesta kirjoituksesta |
| `sc_signal_resolved` | usea ajuri, 0/1/X/Z |
| `sc_fifo<T>` | jono: `read`, `write`, `nb_read`, `nb_write` |
| `sc_mutex`, `sc_semaphore` | resurssien varaus |
| `sc_clock` | kello: jakso, pulssisuhde, alkuhetki |
| oma `sc_prim_channel` | `request_update()` ja `update()` |

# Bittitarkat tyypit

| Tyyppi | Huom. |
|--------|-------|
| `sc_int<W>`, `sc_uint<W>` | W ≤ 64, nopea; välitulos 64 bittiä |
| `sc_bigint<W>`, `sc_biguint<W>` | mielivaltainen leveys |
| `sc_bv<W>`, `sc_lv<W>` | bitit; neliarvoinen logiikka |
| `x.range(h, l)`, `x[i]`, `(a, b)` | kenttä, bitti, liitos |
| `sc_fixed<W, I, Q, O>` | etumerkillinen kiintopiste, Q1.15 = `<16, 1>` |
| `SC_TRN`, `SC_RND`, `SC_RND_CONV` | katkaisu, pyöristys, parilliseen |
| `SC_WRAP`, `SC_SAT` | kierto, kyllästys |
| `sc_fixed_fast` | enintään 53 bittiä, nopea |

Tarkka tulo: W1 + W2 bittiä, I1 + I2 kokonaisbittiä. Summaan N tulosta:
log₂ N suojabittiä.

# TLM-2.0

```{.cpp tiedosto="esimerkit/mallit/siirto.hpp" osa="siirto"}
```

| Kenttä | Funktio |
|--------|---------|
| komento | `set_command(TLM_READ_COMMAND)` |
| osoite | `set_address(a)` |
| data | `set_data_ptr(p)`, `set_data_length(n)` |
| suoratoisto | `set_streaming_width(n)` |
| tavumaski | `set_byte_enable_ptr(p)` |
| vastaus | `set_response_status(...)`, `is_response_error()` |
| DMI-vihje | `set_dmi_allowed(true)`, `is_dmi_allowed()` |

| Socket (`tlm_utils`) | Käyttö |
|----------------------|--------|
| `simple_initiator_socket<M>` | aloittaja |
| `simple_target_socket<M>` | kohde; `register_b_transport` ym. |
| `multi_passthrough_target_socket<M>` | väylä: monta aloittajaa |
| `multi_passthrough_initiator_socket<M>` | väylä: monta kohdetta |

| Kutsu | Tyyli |
|-------|-------|
| `b_transport(gp, viive)` | LT: kohde lisää viiveen, aloittaja odottaa |
| `nb_transport_fw/bw(gp, vaihe, viive)` | AT: vaiheet |
| `get_direct_mem_ptr(gp, dmi)` | DMI |
| `invalidate_direct_mem_ptr(a, b)` | DMI:n mitätöinti |
| `transport_dbg(gp)` | debug: ei aikaa, ei sivuvaikutuksia |

# Ajallinen irrottaminen

| `tlm_quantumkeeper` | Merkitys |
|---------------------|----------|
| `set_global_quantum(t)` | kvantti koko mallille |
| `reset()` | paikallinen aika nollaan |
| `inc(t)`, `set(t)`, `get_local_time()` | paikallinen aika |
| `get_current_time()` | `sc_time_stamp()` + paikallinen |
| `need_sync()`, `sync()` | onko kvantti täynnä; odota ja nollaa |

Kohde, jonka vastaus riippuu ajasta, käyttää `sc_time_stamp() + viive`.

# AT: neljä vaihetta

| Vaihe | Suunta | Sääntö |
|-------|--------|--------|
| `BEGIN_REQ` | → | yksi pyyntö kerrallaan |
| `END_REQ` | ← | aloittaja saa lähettää seuraavan |
| `BEGIN_RESP` | ← | yksi vastaus kerrallaan |
| `END_RESP` | → | kohde saa lähettää seuraavan |

Paluuarvot: `TLM_ACCEPTED`, `TLM_UPDATED`, `TLM_COMPLETED`. Viive
vaiheille `peq_with_cb_and_phase`; payloadin elinikä `acquire()`,
`release()` ja `tlm_mm_interface`.

# Vastaavuus RTL:n kanssa

| Askel | Tapa |
|-------|------|
| RTL SystemC:hen | `verilator --sc`, portit `bool` / `uint32_t` |
| odotetut tulokset | bittitarkka malli, jono viiveen yli |
| herätteet | impulssi, pahin tapaus, satunnainen kiinteällä siemenellä |
| vertailu | tarkka yhtäsuuruus, ei toleranssia |
