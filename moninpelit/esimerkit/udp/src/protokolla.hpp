// Lukitusaskelpelin UDP-protokolla: viestit tavuiksi ja takaisin sekä
// pistokkeen apufunktiot. Kaikki luvut verkkotavujärjestyksessä.
#pragma once
#include <arpa/inet.h>
#include <netinet/in.h>
#include <poll.h>
#include <sys/socket.h>
#include <unistd.h>

#include <array>
#include <cstdint>
#include <optional>
#include <stdexcept>
#include <vector>

#include "../../yhteinen/kaksintaistelu.hpp"
#include "../../yhteinen/verkko.hpp"

constexpr std::uint32_t RUUTUJA = 600;
constexpr std::uint32_t IKKUNA = 8;  // toistettujen syötteiden määrä

// Pelaajan syötteet ruuduittain siemenestä (kuten luvussa 9).
inline std::vector<Syote> syotteet(std::uint64_t siemen) {
    Pcg32 r(siemen);
    std::vector<Syote> v(RUUTUJA);
    Syote s = 0;
    for (Syote& x : v) {
        if (r.valilta(15) == 0) {
            s = static_cast<Syote>(r.valilta(8));
        }
        x = s;
    }
    return v;
}

// @alku viestit
enum Laji : std::uint8_t { SYOTE = 1, TILA = 2, LOPPU = 3 };

// Asiakas -> palvelin: pelaaja, seuraava lähetettävä ruutu ja IKKUNA
// viimeisintä syötettä. Hukattu paketti korvautuu seuraavalla.
struct SyoteViesti {
    std::uint8_t pelaaja;
    std::uint32_t seuraava;           // syötteet ruuduille < seuraava
    std::array<Syote, IKKUNA> syote;  // ruudut seuraava-IKKUNA..-1
};

// Palvelin -> asiakkaat: vahvistettujen ruutujen määrä, tilan
// tarkistussumma ja molempien syötteet viimeisille IKKUNA ruudulle.
struct TilaViesti {
    std::uint8_t laji;  // TILA tai LOPPU
    std::uint32_t ruutuja;
    std::uint32_t summa;
    std::array<std::array<Syote, 2>, IKKUNA> syote;
};
// @loppu viestit

// @alku sarjallistus
class Puskuri {
public:
    void u8(std::uint8_t v) { tavut.push_back(v); }
    void u32(std::uint32_t v) {
        for (int i = 3; i >= 0; --i) {
            tavut.push_back(static_cast<std::uint8_t>(v >> (8 * i)));
        }
    }
    std::uint8_t lue_u8() { return tavut.at(paikka++); }
    std::uint32_t lue_u32() {
        std::uint32_t v = 0;
        for (int i = 0; i < 4; ++i) {
            v = (v << 8) | tavut.at(paikka++);
        }
        return v;
    }
    std::vector<std::uint8_t> tavut;
    std::size_t paikka = 0;
};

inline Puskuri kirjoita(const SyoteViesti& v) {
    Puskuri p;
    p.u8(SYOTE);
    p.u8(v.pelaaja);
    p.u32(v.seuraava);
    for (Syote s : v.syote) {
        p.u8(s);
    }
    return p;
}

inline Puskuri kirjoita(const TilaViesti& v) {
    Puskuri p;
    p.u8(v.laji);
    p.u32(v.ruutuja);
    p.u32(v.summa);
    for (const auto& pari : v.syote) {
        p.u8(pari[0]);
        p.u8(pari[1]);
    }
    return p;
}
// @loppu sarjallistus

inline SyoteViesti lue_syote(Puskuri& p) {
    SyoteViesti v{};
    v.pelaaja = p.lue_u8();
    v.seuraava = p.lue_u32();
    for (Syote& s : v.syote) {
        s = p.lue_u8();
    }
    return v;
}

inline TilaViesti lue_tila(Puskuri& p, std::uint8_t laji) {
    TilaViesti v{};
    v.laji = laji;
    v.ruutuja = p.lue_u32();
    v.summa = p.lue_u32();
    for (auto& pari : v.syote) {
        pari[0] = p.lue_u8();
        pari[1] = p.lue_u8();
    }
    return v;
}

// UDP-pistoke, joka suljetaan automaattisesti (RAII).
class Pistoke {
public:
    Pistoke() : fd_(socket(AF_INET, SOCK_DGRAM, 0)) {
        if (fd_ < 0) {
            throw std::runtime_error("socket");
        }
    }
    ~Pistoke() { close(fd_); }
    Pistoke(const Pistoke&) = delete;
    Pistoke& operator=(const Pistoke&) = delete;

    void sido(std::uint16_t portti) {
        sockaddr_in osoite{};
        osoite.sin_family = AF_INET;
        osoite.sin_port = htons(portti);
        osoite.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
        if (bind(fd_, reinterpret_cast<sockaddr*>(&osoite),
                 sizeof osoite) < 0) {
            throw std::runtime_error("bind");
        }
    }
    std::uint16_t portti() const {
        sockaddr_in osoite{};
        socklen_t koko = sizeof osoite;
        getsockname(fd_, reinterpret_cast<sockaddr*>(&osoite), &koko);
        return ntohs(osoite.sin_port);
    }
    void laheta(const Puskuri& p, const sockaddr_in& kohde) const {
        sendto(fd_, p.tavut.data(), p.tavut.size(), 0,
               reinterpret_cast<const sockaddr*>(&kohde), sizeof kohde);
    }
    // Odottaa enintään 'ms' millisekuntia yhtä datagrammia.
    std::optional<Puskuri> vastaanota(int ms, sockaddr_in* lahettaja) {
        pollfd p{fd_, POLLIN, 0};
        if (poll(&p, 1, ms) <= 0) {
            return std::nullopt;
        }
        Puskuri b;
        b.tavut.resize(512);
        socklen_t koko = sizeof *lahettaja;
        const auto n =
            recvfrom(fd_, b.tavut.data(), b.tavut.size(), 0,
                     reinterpret_cast<sockaddr*>(lahettaja), &koko);
        if (n <= 0) {
            return std::nullopt;
        }
        b.tavut.resize(static_cast<std::size_t>(n));
        return b;
    }

private:
    int fd_;
};

inline sockaddr_in paikallinen(std::uint16_t portti) {
    sockaddr_in o{};
    o.sin_family = AF_INET;
    o.sin_port = htons(portti);
    o.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    return o;
}
