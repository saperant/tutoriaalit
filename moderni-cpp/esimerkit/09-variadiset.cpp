#include <print>
#include <string>

// @alku summa
template <typename... Arvot>
auto summa(const Arvot&... arvot)
{
    return (arvot + ... + 0);   // fold-lauseke
}
// @loppu summa

// @alku kaikki
template <typename... Arvot>
bool kaikki_positiivisia(const Arvot&... arvot)
{
    return ((arvot > 0) && ...);
}
// @loppu kaikki

// @alku tulosta
template <typename Ensimmainen, typename... Loput>
void tulosta_kaikki(const Ensimmainen& eka, const Loput&... loput)
{
    std::print("{}", eka);
    ((std::print(", {}", loput)), ...);
    std::println("  ({} argumenttia)", 1 + sizeof...(loput));
}
// @loppu tulosta

int main()
{
    // @alku kaytto
    std::println("{}", summa(1, 2, 3, 4));
    std::println("{}", summa(1.5, 2));
    std::println("{}", summa());
    std::println("{} {}", kaikki_positiivisia(1, 2.5, 3),
                 kaikki_positiivisia(1, -2));
    tulosta_kaikki("a", 1, 2.5, std::string{"merkkijono"});
    // @loppu kaytto
}
