#include <algorithm>
#include <cstddef>
#include <memory>
#include <print>
#include <utility>

// @alku luokka
class Puskuri {
public:
    explicit Puskuri(std::size_t koko)
        : koko_{koko}, data_{new int[koko]{}}
    {
    }

    ~Puskuri() { delete[] data_; }

    // Kopiomuodostin: varataan oma muisti ja kopioidaan sisältö.
    Puskuri(const Puskuri& toinen)
        : koko_{toinen.koko_}, data_{new int[toinen.koko_]}
    {
        std::copy_n(toinen.data_, koko_, data_);
        std::println("  kopiomuodostin");
    }

    // Siirtomuodostin: otetaan toisen muisti ja jätetään se tyhjäksi.
    Puskuri(Puskuri&& toinen) noexcept
        : koko_{std::exchange(toinen.koko_, 0)},
          data_{std::exchange(toinen.data_, nullptr)}
    {
        std::println("  siirtomuodostin");
    }

    // Yhteinen sijoitus kopiolle ja siirrolle ("copy-and-swap").
    Puskuri& operator=(Puskuri toinen) noexcept
    {
        std::swap(koko_, toinen.koko_);
        std::swap(data_, toinen.data_);
        std::println("  sijoitus");
        return *this;
    }

    std::size_t koko() const { return koko_; }

private:
    std::size_t koko_;
    int* data_;
};
// @loppu luokka

// @alku tehdas
Puskuri tee_puskuri()
{
    return Puskuri{100};
}
// @loppu tehdas

int main()
{
    // @alku kaytto
    std::println("1. luonti");
    Puskuri a{10};

    std::println("2. kopio");
    Puskuri b = a;

    std::println("3. siirto");
    Puskuri c = std::move(a);
    std::println("  a.koko() = {}, c.koko() = {}", a.koko(), c.koko());

    std::println("4. sijoitus väliaikaisesta");
    b = Puskuri{20};

    std::println("5. palautus funktiosta");
    Puskuri d = tee_puskuri();
    std::println("  d.koko() = {}", d.koko());
    // @loppu kaytto
}
