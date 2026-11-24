// pybind11-laajennus: C++-luokka Python-luokaksi ja C++-poikkeus
// Python-poikkeukseksi.
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <cmath>
#include <format>
#include <stdexcept>
#include <vector>

namespace py = pybind11;

// @alku luokka
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

    void lisaa_kaikki(const std::vector<double> &arvot)
    {
        for (double x : arvot)
            lisaa(x);
    }

    double keskiarvo() const
    {
        if (n_ == 0)
            throw TyhjaOtos("otos on tyhjä");
        return keskiarvo_;
    }

    double hajonta() const
    {
        if (n_ < 2)
            throw TyhjaOtos("hajontaan tarvitaan kaksi arvoa");
        return std::sqrt(m2_ / static_cast<double>(n_ - 1));
    }

    std::size_t maara() const { return n_; }

private:
    std::size_t n_ = 0;
    double keskiarvo_ = 0.0;
    double m2_ = 0.0;
};
// @loppu luokka

// @alku moduuli
PYBIND11_MODULE(mittari, m)
{
    m.doc() = "Juokseva tilasto (Welfordin algoritmi)";

    py::register_exception<TyhjaOtos>(m, "TyhjaOtos", PyExc_ValueError);

    py::class_<Tilasto>(m, "Tilasto")
        .def(py::init<>())
        .def("lisaa", &Tilasto::lisaa, py::arg("x"),
             "Lisää yhden havainnon.")
        .def("lisaa_kaikki", &Tilasto::lisaa_kaikki, py::arg("arvot"),
             "Lisää havainnot listasta (lista kopioidaan).")
        .def_property_readonly("keskiarvo", &Tilasto::keskiarvo)
        .def_property_readonly("hajonta", &Tilasto::hajonta)
        .def("__len__", &Tilasto::maara)
        .def("__repr__", [](const Tilasto &t) {
            return std::format("Tilasto(n={})", t.maara());
        });

    m.def("keskiarvo", [](const std::vector<double> &arvot) {
        Tilasto t;
        t.lisaa_kaikki(arvot);
        return t.keskiarvo();
    }, py::arg("arvot"));
}
// @loppu moduuli
