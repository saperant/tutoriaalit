// laskuri.hpp: dynaamisten muistinvarausten laskuri.
//
// Korvaa ohjelman globaalit operator new- ja delete-funktiot versioilla,
// jotka laskevat varaukset ja varatut tavut ennen kuin ne kutsuvat
// mallocia. Otsake otetaan mukaan vain yhteen käännösyksikköön, koska
// korvaavia funktioita saa olla ohjelmassa yksi kappale. Laskuri ei ole
// säieturvallinen; esimerkit ovat yksisäikeisiä.
#ifndef LASKURI_HPP
#define LASKURI_HPP

#include <cstddef>
#include <cstdlib>
#include <new>

// @alku laskuri
namespace laskuri {

inline std::size_t varauksia = 0;
inline std::size_t tavuja = 0;

// Laskee varaukset olion elinaikana.
class Jakso {
public:
    Jakso() : alku_varauksia_{varauksia}, alku_tavuja_{tavuja} {}
    std::size_t varaukset() const { return varauksia - alku_varauksia_; }
    std::size_t tavut() const { return tavuja - alku_tavuja_; }

private:
    std::size_t alku_varauksia_;
    std::size_t alku_tavuja_;
};

inline void* varaa(std::size_t koko, std::size_t tasaus)
{
    ++varauksia;
    tavuja += koko;
    std::size_t pyoristetty = (koko + tasaus - 1) / tasaus * tasaus;
    void* p = tasaus <= alignof(std::max_align_t)
                  ? std::malloc(koko == 0 ? 1 : koko)
                  : std::aligned_alloc(tasaus, pyoristetty);
    if (p == nullptr) {
        throw std::bad_alloc{};
    }
    return p;
}

}  // namespace laskuri

void* operator new(std::size_t koko)
{
    return laskuri::varaa(koko, alignof(std::max_align_t));
}

void* operator new(std::size_t koko, std::align_val_t tasaus)
{
    return laskuri::varaa(koko, static_cast<std::size_t>(tasaus));
}

void operator delete(void* p) noexcept { std::free(p); }
void operator delete(void* p, std::size_t) noexcept { std::free(p); }
void operator delete(void* p, std::align_val_t) noexcept { std::free(p); }
void operator delete(void* p, std::size_t, std::align_val_t) noexcept
{
    std::free(p);
}
// @loppu laskuri

#endif
