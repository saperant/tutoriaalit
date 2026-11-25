#include <cstddef>
#include <numeric>

#include "suodin.hpp"

// @alku cpp
namespace suodin {
// Ylikuormitetut funktiot: nimeen koodataan nimiavaruus ja parametrit.
double keskiarvo(const double *arvot, std::size_t n)
{
    return std::accumulate(arvot, arvot + n, 0.0) / static_cast<double>(n);
}
int keskiarvo(int a, int b) { return (a + b) / 2; }
}  // namespace suodin

// C-rajapinta: nimi ilman koristelua, sisällä tavallista C++:aa.
double suodin_keskiarvo(const double *arvot, int n)
{
    return suodin::keskiarvo(arvot, static_cast<std::size_t>(n));
}
// @loppu cpp
