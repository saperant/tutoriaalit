#include <cstdio>
#include <memory>
#include <print>
#include <stdexcept>
#include <string>
#include <utility>

// @alku jaljitin
class Jaljitin {
public:
    explicit Jaljitin(std::string nimi) : nimi_{std::move(nimi)}
    {
        std::println("  hankitaan {}", nimi_);
    }
    ~Jaljitin() { std::println("  vapautetaan {}", nimi_); }

    Jaljitin(const Jaljitin&) = delete;
    Jaljitin& operator=(const Jaljitin&) = delete;

private:
    std::string nimi_;
};
// @loppu jaljitin

// @alku poikkeus
void kasittele(bool epaonnistu)
{
    Jaljitin a{"A"};
    Jaljitin b{"B"};
    if (epaonnistu) {
        throw std::runtime_error{"jokin meni pieleen"};
    }
    std::println("  käsittely valmis");
}
// @loppu poikkeus

// @alku tiedosto
struct SuljeTiedosto {
    void operator()(std::FILE* f) const
    {
        std::fclose(f);
        std::println("  tiedosto suljettu");
    }
};
using Tiedosto = std::unique_ptr<std::FILE, SuljeTiedosto>;

void kirjoita_valiaikaiseen()
{
    Tiedosto f{std::tmpfile()};
    if (!f) {
        throw std::runtime_error{"tiedostoa ei voitu avata"};
    }
    std::fputs("RAII toimii myös C-rajapintojen kanssa\n", f.get());
    std::println("  kirjoitettu");
}   // fclose kutsutaan tässä automaattisesti
// @loppu tiedosto

int main()
{
    // @alku kaytto
    std::println("Onnistuva kutsu:");
    kasittele(false);

    std::println("Epäonnistuva kutsu:");
    try {
        kasittele(true);
    } catch (const std::exception& e) {
        std::println("  virhe: {}", e.what());
    }

    std::println("Tiedosto:");
    kirjoita_valiaikaiseen();
    // @loppu kaytto
}
