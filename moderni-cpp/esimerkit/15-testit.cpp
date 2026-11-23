#include <chrono>
#include <format>
#include <optional>
#include <print>
#include <source_location>
#include <string>
#include <string_view>
#include <vector>

// @alku testattava
// Jäsentää keston muodossa "1h30m", "45m" tai "2h".
std::optional<std::chrono::minutes> jasenna_kesto(std::string_view s)
{
    using namespace std::chrono;
    minutes tulos{0};
    bool tunnit = false;
    bool minuutit = false;
    while (!s.empty()) {
        int luku = 0;
        std::size_t i = 0;
        while (i < s.size() && s[i] >= '0' && s[i] <= '9' && luku < 100000) {
            luku = luku * 10 + (s[i] - '0');
            ++i;
        }
        if (i == 0 || i == s.size()) {
            return std::nullopt;   // numero tai yksikkö puuttuu
        }
        if (s[i] == 'h' && !tunnit && !minuutit) {
            tulos += hours{luku};
            tunnit = true;
        } else if (s[i] == 'm' && !minuutit) {
            tulos += minutes{luku};
            minuutit = true;
        } else {
            return std::nullopt;
        }
        s.remove_prefix(i + 1);
    }
    if (!tunnit && !minuutit) {
        return std::nullopt;
    }
    return tulos;
}
// @loppu testattava

// @alku kehys
struct Testi {
    std::string_view nimi;
    void (*funktio)();
};

// Funktion sisäinen staattinen muuttuja alustetaan ensimmäisellä
// kutsulla, joten rekisteröinti toimii riippumatta globaalien olioiden
// alustusjärjestyksestä.
std::vector<Testi>& testit()
{
    static std::vector<Testi> kaikki;
    return kaikki;
}

struct Rekisteroi {
    Rekisteroi(std::string_view nimi, void (*f)())
    {
        testit().push_back({nimi, f});
    }
};

struct Epaonnistui {
    std::string viesti;
};

void odota(bool ehto, std::string_view lauseke,
           std::source_location paikka = std::source_location::current())
{
    if (!ehto) {
        throw Epaonnistui{std::format("rivi {}: {}", paikka.line(), lauseke)};
    }
}

#define TESTI(nimi)                                   \
    static void nimi();                               \
    static const Rekisteroi rekisteri_##nimi{#nimi, nimi}; \
    static void nimi()
#define ODOTA(ehto) odota((ehto), #ehto)
// @loppu kehys

// @alku testit
using namespace std::chrono_literals;

TESTI(tunnit_ja_minuutit)
{
    ODOTA(jasenna_kesto("1h30m") == 90min);
    ODOTA(jasenna_kesto("2h") == 120min);
    ODOTA(jasenna_kesto("45m") == 45min);
}

TESTI(tyhja_ja_pelkka_numero_hylataan)
{
    ODOTA(!jasenna_kesto(""));
    ODOTA(!jasenna_kesto("90"));
}

TESTI(yksikko_vain_kerran_ja_oikeassa_jarjestyksessa)
{
    ODOTA(!jasenna_kesto("1h1h"));
    ODOTA(!jasenna_kesto("30m1h"));
}

TESTI(tuntematon_merkki_hylataan)
{
    ODOTA(!jasenna_kesto("-5m"));
    ODOTA(!jasenna_kesto("5s"));
    ODOTA(!jasenna_kesto("h"));
}
// @loppu testit

// @alku ajo
int main()
{
    int lapi = 0;
    for (const auto& t : testit()) {
        try {
            t.funktio();
            std::println("ok      {}", t.nimi);
            ++lapi;
        } catch (const Epaonnistui& e) {
            std::println("VIRHE   {}: {}", t.nimi, e.viesti);
        }
    }
    std::println("{}/{} testiä läpi", lapi, testit().size());
    return lapi == static_cast<int>(testit().size()) ? 0 : 1;
}
// @loppu ajo
