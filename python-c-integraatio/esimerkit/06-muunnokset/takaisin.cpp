// Python-koodi C++:n kutsumana: tallennettu takaisinkutsu ja
// virtuaalifunktion ylikirjoitus Pythonista.
#include <pybind11/functional.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <functional>
#include <utility>
#include <vector>

namespace py = pybind11;

// @alku funktio
// C++-luokka säilyttää kutsuttavan std::function-oliona. pybind11
// käärii Python-funktion olioon, joka omistaa viitteen siihen, joten
// funktio pysyy elossa niin kauan kuin hälytin.
class Halytin {
  public:
    explicit Halytin(double raja) : raja_{raja} {}

    void kun_ylittyy(std::function<void(double)> kasittelija)
    {
        kasittelija_ = std::move(kasittelija);
    }

    int syota(const std::vector<double> &arvot) const
    {
        int ylityksia = 0;
        for (double x : arvot) {
            if (x > raja_ && kasittelija_) {
                kasittelija_(x);       // C++ kutsuu Pythonia
                ++ylityksia;
            }
        }
        return ylityksia;
    }

  private:
    double raja_;
    std::function<void(double)> kasittelija_;
};
// @loppu funktio

// @alku trampoliini
// C++-rajapinta, jonka toteutus voi tulla Pythonista.
class Suodin {
  public:
    virtual ~Suodin() = default;
    virtual double kasittele(double x) const = 0;
};

// Trampoliini: C++:n virtuaalikutsu ohjataan Python-olion metodille.
// Jos Python-luokka ei määrittele metodia, kutsu on virhe (PURE).
class PySuodin : public Suodin {
  public:
    double kasittele(double x) const override
    {
        PYBIND11_OVERRIDE_PURE(double, Suodin, kasittele, x);
    }
};

// Tavallista C++:aa, joka ei tiedä Pythonista mitään.
double summa_suodatettuna(const Suodin &suodin,
                          const std::vector<double> &arvot)
{
    double summa = 0.0;
    for (double x : arvot)
        summa += suodin.kasittele(x);
    return summa;
}
// @loppu trampoliini

// @alku sidonta
PYBIND11_MODULE(takaisin, m)
{
    using namespace py::literals;
    py::class_<Halytin>(m, "Halytin")
        .def(py::init<double>(), "raja"_a)
        .def("kun_ylittyy", &Halytin::kun_ylittyy, "kasittelija"_a)
        .def("syota", &Halytin::syota, "arvot"_a);

    // Toinen malliparametri kertoo trampoliinin, jonka pybind11 luo,
    // kun luokka peritään Pythonissa.
    py::class_<Suodin, PySuodin>(m, "Suodin")
        .def(py::init<>())
        .def("kasittele", &Suodin::kasittele, "x"_a);
    m.def("summa_suodatettuna", &summa_suodatettuna, "suodin"_a, "arvot"_a);
}
// @loppu sidonta
