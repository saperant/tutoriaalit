// Objektipooli: ammukset varataan kerran, ja pelin aikana ne vain
// otetaan käyttöön ja palautetaan. Muistinvaraukset lasketaan
// korvaamalla globaali operator new.
#include <array>
#include <cstdlib>
#include <memory>
#include <new>
#include <print>
#include <vector>

static long varauksia = 0;

void* operator new(std::size_t koko) {
    ++varauksia;
    if (void* p = std::malloc(koko ? koko : 1)) {
        return p;
    }
    throw std::bad_alloc();
}
void operator delete(void* p) noexcept { std::free(p); }
void operator delete(void* p, std::size_t) noexcept { std::free(p); }

struct Ammus {
    double x = 0, y = 0, vx = 0, vy = 0;
    double elinaika = 0;
};

// @alku pooli
template <typename T, std::size_t N>
class Pooli {
public:
    Pooli() {
        for (std::size_t i = 0; i < N; ++i) {
            seuraava_[i] = static_cast<int>(i) + 1;  // vapaiden lista
        }
        seuraava_[N - 1] = -1;
    }
    // Palauttaa nullptr, jos pooli on täynnä: pelisuunnittelun
    // päätös (vanhin ammus pois, uusi jää syntymättä tai pooli kasvaa).
    T* ota() {
        if (vapaa_ < 0) {
            return nullptr;
        }
        const int i = vapaa_;
        vapaa_ = seuraava_[i];
        kaytossa_[i] = true;
        alkiot_[i] = T{};
        return &alkiot_[i];
    }
    void palauta(T* p) {
        const auto i = static_cast<int>(p - alkiot_.data());
        kaytossa_[i] = false;
        seuraava_[i] = vapaa_;
        vapaa_ = i;
    }
    template <typename F>
    void kaikille(F&& f) {
        for (std::size_t i = 0; i < N; ++i) {
            if (kaytossa_[i]) {
                f(alkiot_[i]);
            }
        }
    }

private:
    std::array<T, N> alkiot_{};
    std::array<int, N> seuraava_{};
    std::array<bool, N> kaytossa_{};
    int vapaa_ = 0;
};
// @loppu pooli

int main() {
    constexpr double dt = 1.0 / 60.0;
    {
        varauksia = 0;
        std::vector<std::unique_ptr<Ammus>> ammukset;
        ammukset.reserve(64);
        for (int ruutu = 0; ruutu < 600; ++ruutu) {
            if (ruutu % 6 == 0) {
                ammukset.push_back(std::make_unique<Ammus>(
                    Ammus{0, 0, 300, 0, 0.5}));
            }
            std::erase_if(ammukset, [&](auto& a) {
                a->x += a->vx * dt;
                return (a->elinaika -= dt) <= 0.0;
            });
        }
        std::println("new jokaiselle ammukselle: {} varausta", varauksia);
    }
    {
        // @alku kaytto
        static Pooli<Ammus, 64> pooli;  // varattu ennen pelisilmukkaa
        varauksia = 0;
        for (int ruutu = 0; ruutu < 600; ++ruutu) {
            if (ruutu % 6 == 0) {
                if (Ammus* a = pooli.ota()) {
                    *a = {0, 0, 300, 0, 0.5};
                }
            }
            pooli.kaikille([&](Ammus& a) {
                a.x += a.vx * dt;
                if ((a.elinaika -= dt) <= 0.0) {
                    pooli.palauta(&a);
                }
            });
        }
        // @loppu kaytto
        std::println("pooli: {} varausta", varauksia);
    }
}
