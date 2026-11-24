// Sama juokseva tilasto nanobindilla. Rakenne on lähes sama kuin
// pybind11:ssä: nimiavaruus nb ja otsikot ovat eri.
#include <nanobind/nanobind.h>
#include <nanobind/stl/string.h>
#include <nanobind/stl/vector.h>

#include <cmath>
#include <format>
#include <stdexcept>
#include <vector>

namespace nb = nanobind;

class TyhjaOtos : public std::runtime_error {
    using std::runtime_error::runtime_error;
};

class Tilasto {
public:
    void lisaa(double x)
    {
        if (!std::isfinite(x))
            throw std::invalid_argument("arvon on oltava äärellinen");
        ++n_;
        double d = x - keskiarvo_;
        keskiarvo_ += d / static_cast<double>(n_);
        m2_ += d * (x - keskiarvo_);
    }
    double keskiarvo() const
    {
        if (n_ == 0)
            throw TyhjaOtos("otos on tyhjä");
        return keskiarvo_;
    }
    std::size_t maara() const { return n_; }

private:
    std::size_t n_ = 0;
    double keskiarvo_ = 0.0;
    double m2_ = 0.0;
};

// @alku moduuli
NB_MODULE(tilasto_nb, m)
{
    nb::exception<TyhjaOtos>(m, "TyhjaOtos", PyExc_ValueError);

    nb::class_<Tilasto>(m, "Tilasto")
        .def(nb::init<>())
        .def("lisaa", &Tilasto::lisaa, nb::arg("x"))
        .def("lisaa_kaikki", [](Tilasto &t, const std::vector<double> &v) {
            for (double x : v)
                t.lisaa(x);
        }, nb::arg("arvot"))
        .def_prop_ro("keskiarvo", &Tilasto::keskiarvo)
        .def("__len__", &Tilasto::maara)
        .def("__repr__", [](const Tilasto &t) {
            return std::format("Tilasto(n={})", t.maara());
        });
}
// @loppu moduuli
