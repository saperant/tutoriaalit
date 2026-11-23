#include <concepts>
#include <memory>
#include <numbers>
#include <print>
#include <string>
#include <utility>
#include <vector>

// @alku muodot
// Tavallisia arvotyyppejä ilman yhteistä kantaluokkaa.
struct Ympyra {
    double sade;
    double ala() const { return std::numbers::pi * sade * sade; }
    std::string nimi() const { return "ympyrä"; }
};

struct Suorakulmio {
    double leveys, korkeus;
    double ala() const { return leveys * korkeus; }
    std::string nimi() const { return "suorakulmio"; }
};
// @loppu muodot

// @alku pyyhinta
template <typename T>
concept Muotomainen = requires(const T& m) {
    { m.ala() } -> std::convertible_to<double>;
    { m.nimi() } -> std::convertible_to<std::string>;
};

// Tyyppien pyyhintä: Muoto voi säilyttää minkä tahansa Muotomainen-
// tyypin arvona. Virtuaalinen rajapinta on piilotettu toteutukseen,
// joten käyttäjän tyyppien ei tarvitse periä mitään.
class Muoto {
public:
    // Muoto täyttää itsekin konseptin, joten se rajataan pois: muuten
    // kopio voisi kääriä Muodon uuden Muodon sisään.
    template <Muotomainen T>
        requires(!std::same_as<T, Muoto>)
    Muoto(T arvo) : malli_{std::make_unique<Malli<T>>(std::move(arvo))} {}

    Muoto(const Muoto& toinen) : malli_{toinen.malli_->kopio()} {}
    Muoto& operator=(Muoto toinen) noexcept
    {
        std::swap(malli_, toinen.malli_);
        return *this;
    }
    Muoto(Muoto&&) noexcept = default;

    double ala() const { return malli_->ala(); }
    std::string nimi() const { return malli_->nimi(); }

private:
    struct Kasite {
        virtual ~Kasite() = default;
        virtual double ala() const = 0;
        virtual std::string nimi() const = 0;
        virtual std::unique_ptr<Kasite> kopio() const = 0;
    };

    template <typename T>
    struct Malli final : Kasite {
        explicit Malli(T a) : arvo{std::move(a)} {}
        double ala() const override { return arvo.ala(); }
        std::string nimi() const override { return arvo.nimi(); }
        std::unique_ptr<Kasite> kopio() const override
        {
            return std::make_unique<Malli>(arvo);
        }
        T arvo;
    };

    std::unique_ptr<Kasite> malli_;
};
// @loppu pyyhinta

int main()
{
    // @alku kaytto
    std::vector<Muoto> muodot{Ympyra{1.0}, Suorakulmio{2.0, 3.0}};
    muodot.push_back(muodot[0]);   // kopio: arvosemantiikka säilyy
    for (const auto& m : muodot) {
        std::println("{:<12} {:6.2f}", m.nimi(), m.ala());
    }
    // @loppu kaytto
}
