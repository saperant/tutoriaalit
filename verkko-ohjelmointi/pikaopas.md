---
title: Verkko-ohjelmointi
subtitle: Pikaopas · soketit, kehykset, epoll ja vikasietoisuus
---

# TCP-yhteys

| Palvelin | Asiakas |
|------------------------------------|------------------------------------|
| `socket(AF_INET6, SOCK_STREAM, 0)` | `getaddrinfo(isanta, portti, …)` |
| `setsockopt(SO_REUSEADDR)` | silmukka: `socket` + `connect` |
| `bind` + `listen(fd, SOMAXCONN)` | (lähdeportin valitsee ydin) |
| `accept4(fd, …, SOCK_NONBLOCK)` | `send`/`recv` |

- Portti 0 + `getsockname` = ytimen valitsema vapaa portti.
- `htons`/`htonl` kenttiin, `inet_pton`/`inet_ntop` tekstiin,
  `getnameinfo(NI_NUMERICHOST)` takaisin.
- `sockaddr_storage` mahtuu mikä tahansa osoite.
- IPv6 + IPv4 yhdellä soketilla: `::` ja `IPV6_V6ONLY = 0`.

```{.c tiedosto="esimerkit/verkko.h" osa="kuuntele"}
```

# Sulkeminen

| Toiminto | Vastapuoli näkee |
|----------------------------|------------------------------------------|
| `close` / `shutdown(SHUT_WR)` | `recv` = 0 (FIN) |
| kirjoitus suljettuun | 1. onnistuu, 2. `EPIPE` + `SIGPIPE` |
| `SO_LINGER {1, 0}` + `close` | `ECONNRESET` (RST) |
| close lukemattoman datan kanssa | `ECONNRESET` |

- `MSG_NOSIGNAL` tai `signal(SIGPIPE, SIG_IGN)` palvelimessa.
- Ensin sulkeva jää `TIME_WAIT`-tilaan 60 s → `SO_REUSEADDR`.

# Tavuvirta

- `recv` palauttaa ≤ pyydetyn; kaksi `send`ia voi tulla yhtenä.
- Kehys: pituusetuliite (`uint32` big-endian) tai erotin (CRLF).
- Kokoraja ennen `malloc`ia; kesken viestin loppu = virhe.
- `writev` otsake + data; `TCP_NODELAY` pyyntö–vastaukseen.

```{.c tiedosto="esimerkit/verkko.h" osa="kaikki"}
```

# UDP

- `sendto`/`recvfrom`; rajat säilyvät, ei takuita.
- `MSG_TRUNC` → todellinen koko. Maksimi 65 507 B (IPv4),
  käytännössä alle 1200 B.
- `connect` UDP:llä → ICMP-virheet (`ECONNREFUSED` seuraavassa kutsussa).
- Luotettavuus: järjestysnumero, kuittaus, uudelleenlähetys,
  toistojen kuittaus, lopetuksen viive.

# Sarjallistaminen

- Ei rakenteita verkkoon: täyte, tavujärjestys, koot.
- Ei `*(uint32_t *)(p + 1)` → `memcpy` tai bitinsiirrot.
- TLV: tyyppi, pituus, arvo; tuntematon tyyppi ohitetaan.
- Varint: 7 bittiä/tavu, ylin bitti = jatkuu; zigzag negatiivisille.
- Purkaja: `pituus > n - i` ennen lukua; sumea testaus + ASan.

```{.c tiedosto="esimerkit/05-varint.c" osa="varint"}
```

# Moniasiakaspalvelin

| Malli | Kun |
|---------------------|----------------------------------------------|
| `fork` per yhteys | eristys, vähän yhteyksiä; `SIGCHLD` + `waitpid(WNOHANG)` |
| säie per yhteys | jaettu tila lukoin; irrotettu säie, oma argumentti |
| säiepooli | rajattu rinnakkaisuus |
| `epoll`-silmukka | tuhansia yhteyksiä, yksi säie ydintä kohden |

- `fscanf("…\n")` odottaa seuraavaa riviä → `fgets` + `sscanf`.

# epoll

| Kutsu | Tehtävä |
|---------------------------------------|----------------------------------|
| `epoll_create1(EPOLL_CLOEXEC)` | joukko |
| `epoll_ctl(ep, ADD/MOD/DEL, fd, &e)` | `e.events`, `e.data.ptr` = tila |
| `epoll_wait(ep, t, n, ms)` | valmiit; `ms` = seuraava ajastin |

- `EPOLLIN`, `EPOLLOUT` (vain kun jonossa), `EPOLLRDHUP`,
  `EPOLLET` (lue `EAGAIN`iin), `EPOLLONESHOT`, `EPOLLEXCLUSIVE`.
- Kuvaajiksi: `timerfd`, `signalfd`, `eventfd`, `pidfd_open`.
- Vastapaine: lähtevä > raja → poista `EPOLLIN`.
- Ei estäviä kutsuja silmukassa (DNS, levy, laskenta).

# Virheet

| Virhe | Merkitys | Toimi |
|----------------|-------------------------------------|---------------------------|
| `EAGAIN` | estämätön: ei nyt | odota valmiutta |
| `EINTR` | signaali keskeytti | toista |
| `EINPROGRESS` | estämätön `connect` kesken | `poll` + `SO_ERROR` |
| `ECONNREFUSED` | ei kuuntelijaa (RST, ICMP) | ohimenevä: yritä myöhemmin |
| `ECONNRESET` | vastapuoli katkaisi (RST) | sulje, ehkä uudelleen |
| `EPIPE` | kirjoitus suljettuun | sulje |
| `ETIMEDOUT` | keepalive tai uudelleenlähetys luovutti | sulje, ehkä uudelleen |
| `EADDRINUSE` | portti varattu tai `TIME_WAIT` | `SO_REUSEADDR` |
| `EMSGSIZE` | datagrammi liian suuri | pienennä |

# Aikarajat ja uudelleenyritys

- `connect` määräajassa: `SOCK_NONBLOCK` → `EINPROGRESS` → `poll` →
  `SO_ERROR`.
- `SO_RCVTIMEO`/`SO_SNDTIMEO` per kutsu; määräaika koko operaatiolle.
- Keepalive: `SO_KEEPALIVE`, `TCP_KEEPIDLE`, `TCP_KEEPINTVL`,
  `TCP_KEEPCNT`; `TCP_USER_TIMEOUT` kuittaamattomalle datalle.
- Uudelleen vain ohimenevät virheet ja idempotentit operaatiot
  (tai idempotenssiavain).

```{.c tiedosto="esimerkit/10-uudelleenyritys.c" osa="viive"}
```

# Työkalut

| Komento | Näyttää |
|---------------------------------------|----------------------------------|
| `ss -tlnp` | kuuntelijat ja prosessit |
| `ss -tanpi state established` | yhteydet, jonot, RTT |
| `strace -f -e trace=network ./ohj` | sokettikutsut ja virheet |
| `strace -e inject=recv:error=EINTR` | virheen injektointi |
| `tcpdump -i lo -nn port 8080` | segmentit |
| `nc -v 127.0.0.1 8080` | protokolla käsin |
| `tc qdisc add dev lo root netem loss 5%` | häviö (root, nimiavaruus) |
