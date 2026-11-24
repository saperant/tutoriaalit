// Kohtauspino: valikko, peli ja tauko. Vain päällimmäinen kohtaus saa
// syötteen, mutta alemmat voidaan piirtää sen alle (tauko pelin päällä).
#include <memory>
#include <print>
#include <string>
#include <vector>

class Kohtauspino;

// @alku rajapinta
class Kohtaus {
public:
    virtual ~Kohtaus() = default;
    virtual void syote(Kohtauspino& pino, char nappain) = 0;
    virtual void paivita() {}
    virtual std::string piirra() const = 0;
    // Piirretäänkö alla oleva kohtaus (läpinäkyvä kohtaus)?
    virtual bool lapinakyva() const { return false; }
};

class Kohtauspino {
public:
    // Muutokset tehdään vasta ruudun lopussa: kohtaus ei tuhoa itseään
    // kesken oman metodinsa.
    void lisaa(std::unique_ptr<Kohtaus> k) {
        muutokset_.push_back(std::move(k));
    }
    void poista() { muutokset_.push_back(nullptr); }

    void ruutu(char nappain) {
        if (!pino_.empty()) {
            pino_.back()->syote(*this, nappain);
            pino_.back()->paivita();
        }
        for (auto& m : muutokset_) {
            if (m) {
                pino_.push_back(std::move(m));
            } else {
                pino_.pop_back();
            }
        }
        muutokset_.clear();
    }

    std::string piirra() const {
        // Alimmaksi piirretään ylin kohtaus, joka ei ole läpinäkyvä.
        std::size_t alin = pino_.size() - 1;
        while (alin > 0 && pino_[alin]->lapinakyva()) {
            --alin;
        }
        std::string kuva;
        for (std::size_t i = alin; i < pino_.size(); ++i) {
            kuva += (i > alin ? " + " : "") + pino_[i]->piirra();
        }
        return kuva;
    }

private:
    std::vector<std::unique_ptr<Kohtaus>> pino_;
    std::vector<std::unique_ptr<Kohtaus>> muutokset_;  // nullptr = poista
};
// @loppu rajapinta

class Tauko : public Kohtaus {
public:
    void syote(Kohtauspino& p, char n) override {
        if (n == 'p') {
            p.poista();
        }
    }
    std::string piirra() const override { return "[TAUKO]"; }
    bool lapinakyva() const override { return true; }
};

class Peli : public Kohtaus {
public:
    void syote(Kohtauspino& p, char n) override {
        if (n == 'p') {
            p.lisaa(std::make_unique<Tauko>());
        }
    }
    void paivita() override { ++aika_; }
    std::string piirra() const override {
        return "peli (aika " + std::to_string(aika_) + ")";
    }

private:
    int aika_ = 0;
};

class Valikko : public Kohtaus {
public:
    void syote(Kohtauspino& p, char n) override {
        if (n == 'e') {
            p.lisaa(std::make_unique<Peli>());
        }
    }
    std::string piirra() const override { return "valikko"; }
};

int main() {
    Kohtauspino pino;
    pino.lisaa(std::make_unique<Valikko>());
    for (char nappain : std::string("-e--p--p-")) {
        pino.ruutu(nappain);
        std::println("{} -> {}", nappain, pino.piirra());
    }
}
