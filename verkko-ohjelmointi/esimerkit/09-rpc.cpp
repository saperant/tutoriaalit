// Pieni etäproseduurikutsu (RPC) TCP:n päällä. Asiakas lähettää pyynnöt
// peräkkäin odottamatta vastauksia (putkitus), palvelin suorittaa ne
// rinnakkain ja vastaa valmistumisjärjestyksessä. Pyyntötunniste
// yhdistää vastauksen kutsuun, ja määräaika rajaa odotuksen.
// TSAN
#include <poll.h>

#include <chrono>
#include <cstdio>
#include <cstring>
#include <expected>
#include <map>
#include <mutex>
#include <thread>
#include <vector>

#include "verkko.h"

namespace {

// @alku protokolla
// Kehys: pituus (4) | tunniste (4) | metodi tai tila (2) | argumentit.
// Kaikki kentät verkon tavujärjestyksessä.
enum class Metodi : uint16_t { summa = 1, jaa = 2, nuku = 3 };
enum class Virhe : uint16_t {
    ok = 0, tuntematon_metodi = 1, virheellinen_argumentti = 2,
    maaraaika_ylittyi = 100, yhteys_katkesi = 101   // vain asiakkaalla
};

struct Kehys {
    uint32_t tunniste;
    uint16_t koodi;                      // Metodi tai Virhe
    int32_t a, b;
};

bool laheta(int fd, const Kehys &k) {
    uint32_t sanat[4] = {htonl(14), htonl(k.tunniste),
                         htonl(static_cast<uint32_t>(k.a)),
                         htonl(static_cast<uint32_t>(k.b))};
    uint16_t koodi = htons(k.koodi);
    unsigned char b[18];
    std::memcpy(b, &sanat[0], 8);
    std::memcpy(b + 8, &koodi, 2);
    std::memcpy(b + 10, &sanat[2], 8);
    return kirjoita_kaikki(fd, b, sizeof b) == 0;
}

bool vastaanota(int fd, Kehys &k) {
    unsigned char b[18];
    if (lue_tasan(fd, b, sizeof b) != 1) {
        return false;
    }
    uint32_t s[4];
    uint16_t koodi;
    std::memcpy(&s[0], b, 8);
    std::memcpy(&koodi, b + 8, 2);
    std::memcpy(&s[2], b + 10, 8);
    if (ntohl(s[0]) != 14) {
        return false;                    // tämä versio tuntee vain yhden
    }                                    // kehyskoon
    k = {ntohl(s[1]), ntohs(koodi), static_cast<int32_t>(ntohl(s[2])),
         static_cast<int32_t>(ntohl(s[3]))};
    return true;
}
// @loppu protokolla

// @alku palvelin
// Jokainen pyyntö omassa säikeessään. Vastausten kirjoitus sarjallistetaan
// lukolla, jotta kahden säikeen kehykset eivät lomitu.
Kehys suorita(const Kehys &p) {
    Kehys v{p.tunniste, static_cast<uint16_t>(Virhe::ok), 0, 0};
    switch (static_cast<Metodi>(p.koodi)) {
    case Metodi::summa:
        v.a = p.a + p.b;
        break;
    case Metodi::jaa:
        if (p.b == 0) {
            v.koodi = static_cast<uint16_t>(Virhe::virheellinen_argumentti);
        } else {
            v.a = p.a / p.b;
        }
        break;
    case Metodi::nuku:
        std::this_thread::sleep_for(std::chrono::milliseconds(p.a));
        break;
    default:
        v.koodi = static_cast<uint16_t>(Virhe::tuntematon_metodi);
    }
    return v;
}

int palvelin(void *arg) {
    int yhteys = static_cast<int>(TARKISTA(
        accept(*static_cast<int *>(arg), nullptr, nullptr)));
    std::mutex kirjoitus;
    std::vector<std::jthread> tyot;      // jthread liittyy tuhoutuessaan
    Kehys pyynto;
    while (vastaanota(yhteys, pyynto)) {
        tyot.emplace_back([&kirjoitus, yhteys, pyynto] {
            Kehys v = suorita(pyynto);
            std::lock_guard lukko(kirjoitus);
            laheta(yhteys, v);           // asiakas voi olla jo poissa
        });
    }
    tyot.clear();                        // odota keskeneräiset
    close(yhteys);
    return 0;
}
// @loppu palvelin

// @alku asiakas
template <typename T>
using Tulos = std::expected<T, Virhe>;

class Asiakas {
public:
    explicit Asiakas(int fd) : fd_(fd) {}
    ~Asiakas() { close(fd_); }
    Asiakas(const Asiakas &) = delete;
    Asiakas &operator=(const Asiakas &) = delete;

    // Lähettää kutsun ja palauttaa sen tunnisteen; vastausta ei odoteta.
    uint32_t kutsu(Metodi m, int32_t a, int32_t b) {
        uint32_t t = seuraava_++;
        laheta(fd_, {t, static_cast<uint16_t>(m), a, b});
        return t;
    }

    // Odottaa tunnisteen vastausta enintään määräajan. Muiden kutsujen
    // vastaukset talletetaan odottamaan omaa noutoaan.
    Tulos<int32_t> tulos(uint32_t t, std::chrono::milliseconds maaraaika) {
        auto raja = std::chrono::steady_clock::now() + maaraaika;
        while (!saapuneet_.contains(t)) {
            auto jaljella = std::chrono::duration_cast<
                std::chrono::milliseconds>(raja -
                                           std::chrono::steady_clock::now());
            pollfd p{fd_, POLLIN, 0};
            if (jaljella.count() <= 0 ||
                poll(&p, 1, static_cast<int>(jaljella.count())) == 0) {
                return std::unexpected(Virhe::maaraaika_ylittyi);
            }
            Kehys v;
            if (!vastaanota(fd_, v)) {
                return std::unexpected(Virhe::yhteys_katkesi);
            }
            saapumisjarjestys.push_back(v.tunniste);
            saapuneet_[v.tunniste] = v;
        }
        Kehys v = saapuneet_[t];
        saapuneet_.erase(t);
        if (v.koodi != static_cast<uint16_t>(Virhe::ok)) {
            return std::unexpected(static_cast<Virhe>(v.koodi));
        }
        return v.a;
    }

    std::vector<uint32_t> saapumisjarjestys;

private:
    int fd_;
    uint32_t seuraava_ = 1;
    std::map<uint32_t, Kehys> saapuneet_;
};
// @loppu asiakas

const char *nimi(Virhe v) {
    switch (v) {
    case Virhe::tuntematon_metodi: return "tuntematon metodi";
    case Virhe::virheellinen_argumentti: return "virheellinen argumentti";
    case Virhe::maaraaika_ylittyi: return "määräaika ylittyi";
    case Virhe::yhteys_katkesi: return "yhteys katkesi";
    default: return "ok";
    }
}

void tulosta(const char *kutsu, const Tulos<int32_t> &t) {
    if (t) {
        std::printf("%-14s = %d\n", kutsu, *t);
    } else {
        std::printf("%-14s : virhe: %s\n", kutsu, nimi(t.error()));
    }
}

}  // namespace

int main() {
    vahtikoira();
    uint16_t portti;
    int kuuntelija = kuuntele(&portti);
    pid_t pid = kaynnista(palvelin, &kuuntelija);
    {
        // @alku kaytto
        using namespace std::chrono_literals;
        Asiakas a(yhdista(portti));
        uint32_t hidas = a.kutsu(Metodi::nuku, 300, 0);
        uint32_t s = a.kutsu(Metodi::summa, 40, 2);
        uint32_t j = a.kutsu(Metodi::jaa, 7, 0);
        uint32_t x = a.kutsu(static_cast<Metodi>(9), 0, 0);
        tulosta("nuku(300)", a.tulos(hidas, 2s));
        tulosta("summa(40, 2)", a.tulos(s, 2s));
        tulosta("jaa(7, 0)", a.tulos(j, 2s));
        tulosta("metodi 9", a.tulos(x, 2s));
        tulosta("nuku(500)", a.tulos(a.kutsu(Metodi::nuku, 500, 0), 100ms));
        // @loppu kaytto
        std::printf("hidas vastaus saapui viimeisenä: %s\n",
                    a.saapumisjarjestys.back() == hidas ? "kyllä" : "ei");
    }
    close(kuuntelija);
    return odota(pid);
}
