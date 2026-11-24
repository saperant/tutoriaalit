// Tapahtumajono: pelilogiikka ilmoittaa tapahtumista, ja kiinnostuneet
// järjestelmät käsittelevät ne ruudun lopussa. Logiikka ei tunne ääntä,
// pisteitä eikä saavutuksia.
#include <print>
#include <variant>
#include <vector>

// @alku jono
struct KolikkoKeratty { int arvo; };
struct VihollinenKuoli { int tyyppi; };
struct PelaajaOsui { int vahinko; };
using Tapahtuma = std::variant<KolikkoKeratty, VihollinenKuoli, PelaajaOsui>;

class Tapahtumajono {
public:
    void lisaa(Tapahtuma t) { jono_.push_back(t); }

    // Käsittelyn aikana syntyvät uudet tapahtumat menevät seuraavaan
    // kierrokseen, joten käsittelijät eivät kutsu toisiaan sisäkkäin.
    template <typename Kasittelija>
    void kasittele(Kasittelija&& k) {
        std::vector<Tapahtuma> nyt;
        nyt.swap(jono_);
        for (const Tapahtuma& t : nyt) {
            std::visit(k, t);
        }
    }

private:
    std::vector<Tapahtuma> jono_;
};
// @loppu jono

struct Pisteet {
    int summa = 0;
    void operator()(const KolikkoKeratty& t) { summa += t.arvo; }
    void operator()(const VihollinenKuoli& t) { summa += 100 * t.tyyppi; }
    void operator()(const PelaajaOsui&) {}
};

struct Aanet {
    void operator()(const KolikkoKeratty&) { std::println("  ääni: kling"); }
    void operator()(const VihollinenKuoli&) { std::println("  ääni: pum"); }
    void operator()(const PelaajaOsui&) { std::println("  ääni: auts"); }
};

int main() {
    Tapahtumajono jono;
    Pisteet pisteet;
    Aanet aanet;
    for (int ruutu = 0; ruutu < 3; ++ruutu) {
        // Pelilogiikka (tässä kovakoodattu).
        if (ruutu == 0) {
            jono.lisaa(KolikkoKeratty{10});
            jono.lisaa(KolikkoKeratty{10});
        }
        if (ruutu == 2) {
            jono.lisaa(VihollinenKuoli{2});
            jono.lisaa(PelaajaOsui{1});
        }
        std::println("ruutu {}:", ruutu);
        // @alku ruudun-loppu
        jono.kasittele([&](const auto& t) {
            pisteet(t);
            aanet(t);
        });
        // @loppu ruudun-loppu
        std::println("  pisteet {}", pisteet.summa);
    }
}
