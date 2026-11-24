// nanobindin nb::ndarray: rajoitteet kirjoitetaan tyyppiin, ja väärä
// taulukko hylätään jo kutsussa.
#include <nanobind/nanobind.h>
#include <nanobind/ndarray.h>

#include <cstddef>

namespace nb = nanobind;

// @alku ndarray
using Vektori = nb::ndarray<const float, nb::ndim<1>, nb::c_contig,
                            nb::device::cpu>;

double summa(Vektori v)
{
    const float *p = v.data();
    double s = 0.0;
    for (std::size_t i = 0; i < v.shape(0); ++i)
        s += p[i];
    return s;
}

NB_MODULE(kuva_nb, m)
{
    // Oletuksena sopimaton taulukko muunnetaan (kopio); noconvert
    // hylkää sen.
    m.def("summa", &summa, nb::arg("v"));
    m.def("summa_tiukka", &summa, nb::arg("v").noconvert());
}
// @loppu ndarray
