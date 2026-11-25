// Kahvat osoittimien sijaan: resurssiin viitataan indeksillä ja
// sukupolvella, joten vapautettuun resurssiin viittaava kahva
// havaitaan eikä se johda roikkuvaan osoittimeen.
#include <cstdint>
#include <optional>
#include <print>
#include <string>
#include <vector>

// @alku kahva
template <typename T>
class Kahvavarasto {
public:
    struct Kahva {
        std::uint32_t indeksi = 0, sukupolvi = 0;
    };

    Kahva lisaa(T arvo) {
        if (!vapaat_.empty()) {
            const std::uint32_t i = vapaat_.back();
            vapaat_.pop_back();
            paikat_[i].arvo = std::move(arvo);
            return {i, paikat_[i].sukupolvi};
        }
        paikat_.push_back({std::move(arvo), 0});
        return {static_cast<std::uint32_t>(paikat_.size() - 1), 0};
    }

    void poista(Kahva k) {
        if (hae(k)) {
            paikat_[k.indeksi].arvo.reset();
            ++paikat_[k.indeksi].sukupolvi;  // vanhat kahvat vanhenevat
            vapaat_.push_back(k.indeksi);
        }
    }

    T* hae(Kahva k) {
        if (k.indeksi >= paikat_.size()) {
            return nullptr;
        }
        Paikka& p = paikat_[k.indeksi];
        return p.sukupolvi == k.sukupolvi && p.arvo ? &*p.arvo : nullptr;
    }

private:
    struct Paikka {
        std::optional<T> arvo;
        std::uint32_t sukupolvi;
    };
    std::vector<Paikka> paikat_;
    std::vector<std::uint32_t> vapaat_;
};
// @loppu kahva

struct Tekstuuri {
    std::string nimi;
    int leveys, korkeus;
};

int main() {
    Kahvavarasto<Tekstuuri> tekstuurit;
    auto pelaaja = tekstuurit.lisaa({"pelaaja.png", 32, 32});
    auto tausta = tekstuurit.lisaa({"tausta.png", 512, 256});

    // @alku vanheneminen
    auto sprite_viittaa = pelaaja;  // esim. sprite-komponentti
    tekstuurit.poista(pelaaja);     // taso vaihtuu, tekstuuri vapautuu
    auto uusi = tekstuurit.lisaa({"vihollinen.png", 16, 16});

    std::println("uusi indeksi {}, sukupolvi {}", uusi.indeksi,
                 uusi.sukupolvi);
    if (Tekstuuri* t = tekstuurit.hae(sprite_viittaa)) {
        std::println("sprite piirtää: {}", t->nimi);
    } else {
        std::println("spriten tekstuuri on vapautettu");
    }
    // @loppu vanheneminen
    std::println("tausta: {}", tekstuurit.hae(tausta)->nimi);
}
