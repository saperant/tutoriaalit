// Oma luotettavuuskerros UDP:n päälle: jokaisessa paketissa on oma
// sekvenssinumero, viimeisin vastaanotettu numero ja 32 bitin
// kuittauskenttä. Tärkeät tapahtumat lähetetään uudelleen, kunnes
// niiden paketti kuitataan; tilapäivityksiä ei lähetetä uudelleen.
#include <cstdint>
#include <map>
#include <print>
#include <set>
#include <vector>

#include "yhteinen/verkko.hpp"

constexpr bool uudempi(std::uint16_t a, std::uint16_t b) {
    return static_cast<std::int16_t>(static_cast<std::uint16_t>(a - b)) > 0;
}

// @alku paketti
struct Paketti {
    std::uint16_t numero;      // tämän paketin numero
    std::uint16_t kuittaus;    // uusin vastaanotettu numero
    std::uint32_t kentta;      // bitti i: kuittaus - 1 - i saapui
    std::vector<int> tapahtumat;  // luotettavat viestit (tunnisteet)
    // ...lisäksi aina uusin tila, jota ei lähetetä uudelleen
};
// @loppu paketti

class Paa {
public:
    // @alku vastaanotto
    void vastaanota(const Paketti& p) {
        // Kirjataan saapunut numero kuittauskenttään.
        if (!saatu_mitaan_ || uudempi(p.numero, kuittaus_)) {
            const auto siirto =
                static_cast<std::uint16_t>(p.numero - kuittaus_);
            kentta_ = saatu_mitaan_ && siirto <= 32
                          ? (kentta_ << siirto) | (1u << (siirto - 1))
                          : 0;
            kuittaus_ = p.numero;
            saatu_mitaan_ = true;
        } else {
            const auto ero =
                static_cast<std::uint16_t>(kuittaus_ - p.numero);
            if (ero >= 1 && ero <= 32) {
                kentta_ |= 1u << (ero - 1);
            }
        }
        // Vastapuolen kuittaukset: lähetetyt paketit, jotka on saatu.
        kuittaa(p.kuittaus);
        for (unsigned i = 0; i < 32; ++i) {
            if (p.kentta & (1u << i)) {
                kuittaa(static_cast<std::uint16_t>(p.kuittaus - 1 - i));
            }
        }
        // Tapahtumat käsitellään kerran, vaikka ne tulisivat monesti.
        for (int t : p.tapahtumat) {
            if (kasitellyt_.insert(t).second) {
                ++kasitelty;
            } else {
                ++kaksoiskappaleita;
            }
        }
    }
    // @loppu vastaanotto

    // @alku lahetys
    Paketti laheta(std::int64_t nyt) {
        Paketti p{numero_, kuittaus_, kentta_, {}};
        for (auto& [tunniste, viimeksi] : kesken_) {
            if (nyt - viimeksi >= UUDELLEEN_MS) {  // ei joka paketissa
                p.tapahtumat.push_back(tunniste);
                if (viimeksi >= 0) {
                    ++uudelleenlahetyksia;
                }
                viimeksi = nyt;
            }
        }
        lahetetyt_[numero_] = p.tapahtumat;
        ++numero_;
        return p;
    }
    // @loppu lahetys

    void lisaa_tapahtuma(int tunniste) { kesken_[tunniste] = -1'000; }
    bool kaikki_kuitattu() const { return kesken_.empty(); }

    int kasitelty = 0, kaksoiskappaleita = 0, uudelleenlahetyksia = 0;

private:
    static constexpr std::int64_t UUDELLEEN_MS = 150;

    void kuittaa(std::uint16_t numero) {
        const auto it = lahetetyt_.find(numero);
        if (it == lahetetyt_.end()) {
            return;
        }
        for (int t : it->second) {
            kesken_.erase(t);
        }
        lahetetyt_.erase(it);
    }

    std::uint16_t numero_ = 0, kuittaus_ = 0;
    std::uint32_t kentta_ = 0;
    bool saatu_mitaan_ = false;
    std::map<std::uint16_t, std::vector<int>> lahetetyt_;
    std::map<int, std::int64_t> kesken_;  // tapahtuma -> viimeisin lähetys
    std::set<int> kasitellyt_;
};

int main() {
    const Linkki huono{.viive_ms = 40, .varina_ms = 30,
                       .havio_promille = 150};
    Kanava<Paketti> menossa(huono, 1), tulossa(huono, 2);
    Paa asiakas, palvelin;
    int paketteja = 0;
    for (std::int64_t nyt = 0; nyt < 12'000; ++nyt) {
        if (nyt % 200 == 0 && nyt < 10'000) {
            // esim. "poimi esine" tai chat-viesti viidesti sekunnissa
            asiakas.lisaa_tapahtuma(static_cast<int>(nyt / 200));
        }
        if (nyt % 33 == 0) {  // noin 30 pakettia sekunnissa
            menossa.laheta(nyt, asiakas.laheta(nyt));
            tulossa.laheta(nyt, palvelin.laheta(nyt));
            ++paketteja;
        }
        for (const Paketti& p : menossa.vastaanota(nyt)) {
            palvelin.vastaanota(p);
        }
        for (const Paketti& p : tulossa.vastaanota(nyt)) {
            asiakas.vastaanota(p);
        }
    }
    std::println("paketteja suuntaansa {}, hukattu {} ja {}", paketteja,
                 menossa.hukattu(), tulossa.hukattu());
    std::println("tapahtumia käsitelty {}/50, kaksoiskappaleita {}",
                 palvelin.kasitelty, palvelin.kaksoiskappaleita);
    std::println("uudelleenlähetyksiä {}, kaikki kuitattu: {}",
                 asiakas.uudelleenlahetyksia, asiakas.kaikki_kuitattu());
}
