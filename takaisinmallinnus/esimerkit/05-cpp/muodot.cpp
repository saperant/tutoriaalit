// Kohdeohjelma C++:n takaisinmallinnukseen: virtuaalifunktiot, RTTI,
// poikkeukset sekä std::stringin ja std::vectorin muistiasettelu.
#include <cstdio>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>

// @alku luokat
class Muoto {
public:
    virtual ~Muoto() = default;
    virtual double pinta_ala() const = 0;
    virtual const char *nimi() const { return "muoto"; }
};

class Ympyra final : public Muoto {
public:
    explicit Ympyra(double r) : sade_(r) {}
    double pinta_ala() const override { return 3.14159265 * sade_ * sade_; }
    const char *nimi() const override { return "ympyrä"; }

private:
    double sade_;
};

class Suorakulmio : public Muoto {
public:
    Suorakulmio(double l, double k) : leveys_(l), korkeus_(k) {}
    double pinta_ala() const override { return leveys_ * korkeus_; }

private:
    double leveys_;
    double korkeus_;
};
// @loppu luokat

// @alku kaytto
[[gnu::noinline]] double
kokonaisala(const std::vector<std::unique_ptr<Muoto>> &muodot)
{
    double summa = 0.0;
    for (const auto &m : muodot) {
        summa += m->pinta_ala();
    }
    return summa;
}

[[gnu::noinline]] std::unique_ptr<Muoto> luo(const std::string &kuvaus)
{
    if (kuvaus == "ympyra") {
        return std::make_unique<Ympyra>(1.0);
    }
    if (kuvaus == "nelio") {
        return std::make_unique<Suorakulmio>(2.0, 2.0);
    }
    throw std::invalid_argument("tuntematon muoto: " + kuvaus);
}

[[gnu::noinline]] int ympyroita(const std::vector<std::unique_ptr<Muoto>> &m)
{
    int n = 0;
    for (const auto &p : m) {
        n += dynamic_cast<const Ympyra *>(p.get()) != nullptr;
    }
    return n;
}
// @loppu kaytto

int main()
{
    std::vector<std::unique_ptr<Muoto>> muodot;
    const std::vector<std::string> kuvaukset = {"ympyra", "kolmio",
                                                "nelio"};
    for (const auto &k : kuvaukset) {
        try {
            muodot.push_back(luo(k));
        } catch (const std::invalid_argument &virhe) {
            std::printf("virhe: %s\n", virhe.what());
        }
    }
    const std::string lyhyt = "abc";
    const std::string pitka(40, 'x');
    std::printf("ala %.2f, ympyröitä %d, merkkejä %zu\n",
                kokonaisala(muodot), ympyroita(muodot),
                lyhyt.size() + pitka.size());
    return 0;
}
