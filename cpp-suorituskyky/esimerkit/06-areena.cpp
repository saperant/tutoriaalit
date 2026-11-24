// Oma allokaattori: areena, josta varataan peräkkäin ja joka vapautetaan
// kerralla. Sopii lyhytikäisille solmusäiliöille, kuten std::list.
#include <cstddef>
#include <cstdio>
#include <list>
#include <memory>
#include <new>

#include "laskuri.hpp"

// @alku areena
class Areena {
public:
    explicit Areena(std::size_t koko)
        : muisti_{std::make_unique<std::byte[]>(koko)}, koko_{koko} {}

    void* varaa(std::size_t tavuja, std::size_t tasaus)
    {
        std::size_t alku = (kaytetty_ + tasaus - 1) / tasaus * tasaus;
        if (alku + tavuja > koko_) {
            throw std::bad_alloc{};
        }
        kaytetty_ = alku + tavuja;
        return muisti_.get() + alku;
    }
    std::size_t kaytetty() const { return kaytetty_; }

private:
    std::unique_ptr<std::byte[]> muisti_;
    std::size_t koko_;
    std::size_t kaytetty_ = 0;
};

// Allokaattori on kevyt kahva areenaan. Vapautus ei tee mitään: muisti
// palautuu, kun areena tuhoutuu.
template <typename T>
class AreenaAllokaattori {
public:
    using value_type = T;
    explicit AreenaAllokaattori(Areena& a) : areena_{&a} {}
    template <typename U>
    AreenaAllokaattori(const AreenaAllokaattori<U>& muu)
        : areena_{muu.areena()} {}

    T* allocate(std::size_t n)
    {
        return static_cast<T*>(areena_->varaa(n * sizeof(T), alignof(T)));
    }
    void deallocate(T*, std::size_t) {}
    Areena* areena() const { return areena_; }
    bool operator==(const AreenaAllokaattori& muu) const = default;

private:
    Areena* areena_;
};
// @loppu areena

int main()
{
    // @alku kaytto
    Areena areena{1 << 16};
    laskuri::Jakso j;
    {
        std::list<int, AreenaAllokaattori<int>> jono{
            AreenaAllokaattori<int>{areena}};
        for (int i = 0; i < 1000; ++i) {
            jono.push_back(i);
        }
        std::printf("alkioita %zu, areenaa kaytetty %zu tavua\n",
                    jono.size(), areena.kaytetty());
    }
    std::printf("varauksia keosta: %zu\n", j.varaukset());
    // @loppu kaytto
}
