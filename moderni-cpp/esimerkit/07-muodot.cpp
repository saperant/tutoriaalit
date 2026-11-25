#include <memory>
#include <numbers>
#include <print>
#include <string>
#include <vector>

// @alku kanta
class Muoto {
public:
    virtual ~Muoto() = default;
    virtual double ala() const = 0;
    virtual std::string nimi() const { return "muoto"; }
};
// @loppu kanta

// @alku johdetut
class Ympyra final : public Muoto {
public:
    explicit Ympyra(double sade) : sade_{sade} {}
    double ala() const override { return std::numbers::pi * sade_ * sade_; }
    std::string nimi() const override { return "ympyrä"; }

private:
    double sade_;
};

class Suorakulmio : public Muoto {
public:
    Suorakulmio(double leveys, double korkeus)
        : leveys_{leveys}, korkeus_{korkeus} {}
    explicit Suorakulmio(double sivu)
        : Suorakulmio{sivu, sivu} {}   // delegoiva muodostin
    double ala() const override { return leveys_ * korkeus_; }
    std::string nimi() const override { return "suorakulmio"; }

private:
    double leveys_;
    double korkeus_;
};
// @loppu johdetut

int main()
{
    // @alku kaytto
    std::vector<std::unique_ptr<Muoto>> muodot;
    muodot.push_back(std::make_unique<Ympyra>(1.0));
    muodot.push_back(std::make_unique<Suorakulmio>(2.0, 3.0));
    muodot.push_back(std::make_unique<Suorakulmio>(4.0));

    for (const auto& m : muodot) {
        std::println("{:<12} {:6.2f}", m->nimi(), m->ala());
    }
    // @loppu kaytto
}
