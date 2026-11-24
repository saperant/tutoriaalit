// Tyyppimuunnokset kielten rajalla: kopio vai viite, ja kuka pitää
// olion elossa.
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>

#include <cstdint>
#include <vector>

namespace py = pybind11;

// Laskurit (std::vector<int64_t>) on läpinäkymätön: Python näkee saman
// C++-vektorin eikä kopiota. std::vector<double> muunnetaan listaksi.
PYBIND11_MAKE_OPAQUE(std::vector<std::int64_t>)

// @alku kopio
void tuplaa(std::vector<double> &arvot)       // saa kopion listasta
{
    for (double &x : arvot)
        x *= 2.0;
}

void kasvata(std::vector<std::int64_t> &laskurit)   // saa saman olion
{
    for (auto &x : laskurit)
        ++x;
}
// @loppu kopio

// @alku elinaika
class Vahvistus {
public:
    explicit Vahvistus(double kerroin) : kerroin_(kerroin) { ++elossa; }
    Vahvistus(const Vahvistus &) = delete;
    ~Vahvistus() { --elossa; }
    double kasittele(double x) const { return kerroin_ * x; }
    static inline int elossa = 0;

private:
    double kerroin_;
};

class Ketju {
public:
    void lisaa(Vahvistus &v) { vaiheet_.push_back(&v); }   // ei omista
    double aja(double x) const
    {
        for (const Vahvistus *v : vaiheet_)
            x = v->kasittele(x);
        return x;
    }
    Vahvistus &vaihe(std::size_t i) { return *vaiheet_.at(i); }

private:
    std::vector<Vahvistus *> vaiheet_;
};
// @loppu elinaika

PYBIND11_MODULE(muunnos, m)
{
    py::bind_vector<std::vector<std::int64_t>>(m, "Laskurit");
    m.def("tuplaa", &tuplaa);
    m.def("kasvata", &kasvata);

    // @alku sidonta
    py::class_<Vahvistus>(m, "Vahvistus")
        .def(py::init<double>())
        .def("kasittele", &Vahvistus::kasittele)
        .def_property_readonly_static(
            "elossa", [](const py::object &) { return Vahvistus::elossa; });

    py::class_<Ketju>(m, "Ketju")
        .def(py::init<>())
        // Ketju (1) pitää lisätyn vaiheen (2) elossa.
        .def("lisaa", &Ketju::lisaa, py::keep_alive<1, 2>())
        .def("aja", &Ketju::aja)
        // Palautettu viite pitää ketjun elossa.
        .def("vaihe", &Ketju::vaihe,
             py::return_value_policy::reference_internal);
    // @loppu sidonta
}
