#include "tuote.hpp"

// @alku erillinen
bool hinta_ensin_erillinen(const Tuote& a, const Tuote& b)
{
    return a.hinta_snt < b.hinta_snt;
}
// @loppu erillinen
