// Kide-kielen aritmetiikan merkitys. Tulkki ja vakioiden laskostus
// käyttävät samoja funktioita, ja ne vastaavat RISC-V:n käskyjä.
#pragma once

#include <cstdint>
#include <limits>

namespace kide::semantiikka {

// @alku aritmetiikka
// Yhteen-, vähennys- ja kertolasku kiertävät modulo 2^64 kuten
// RISC-V:n add, sub ja mul. C++:ssa etumerkillisen luvun ylivuoto on
// määrittelemätöntä, joten lasketaan etumerkittöminä.
inline std::int64_t summa(std::int64_t a, std::int64_t b) {
    return static_cast<std::int64_t>(static_cast<std::uint64_t>(a)
                                     + static_cast<std::uint64_t>(b));
}
inline std::int64_t erotus(std::int64_t a, std::int64_t b) {
    return static_cast<std::int64_t>(static_cast<std::uint64_t>(a)
                                     - static_cast<std::uint64_t>(b));
}
inline std::int64_t tulo(std::int64_t a, std::int64_t b) {
    return static_cast<std::int64_t>(static_cast<std::uint64_t>(a)
                                     * static_cast<std::uint64_t>(b));
}
inline std::int64_t vastaluku(std::int64_t a) { return erotus(0, a); }

// Jakolasku katkaisee kohti nollaa. Nollalla jako ja pienin luku
// jaettuna -1:llä määritellään kuten RISC-V:n div ja rem tekevät.
constexpr auto kPienin = std::numeric_limits<std::int64_t>::min();

inline std::int64_t osamaara(std::int64_t a, std::int64_t b) {
    if (b == 0) return -1;
    if (a == kPienin && b == -1) return kPienin;
    return a / b;
}
inline std::int64_t jakojaannos(std::int64_t a, std::int64_t b) {
    if (b == 0) return a;
    if (a == kPienin && b == -1) return 0;
    return a % b;
}
// @loppu aritmetiikka

}  // namespace kide::semantiikka
