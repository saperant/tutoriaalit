// Sama laskenta kolmella rajapinnalla: alkio kerrallaan, listana ja
// NumPy-taulukkona.
#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <vector>

namespace py = pybind11;

// @alku rajapinnat
double nelio(double x) { return x * x; }

std::vector<double> neliot_lista(const std::vector<double> &x)
{
    std::vector<double> y(x.size());
    for (std::size_t i = 0; i < x.size(); ++i)
        y[i] = x[i] * x[i];
    return y;                      // muunnetaan takaisin Python-listaksi
}

py::array_t<double> neliot_taulukko(
    py::array_t<double, py::array::c_style> x)
{
    py::array_t<double> y(x.size());
    const double *p = x.data();
    double *q = y.mutable_data();
    for (py::ssize_t i = 0; i < x.size(); ++i)
        q[i] = p[i] * p[i];
    return y;
}
// @loppu rajapinnat

PYBIND11_MODULE(hinta, m)
{
    m.def("nelio", &nelio);
    m.def("neliot_lista", &neliot_lista);
    m.def("neliot_taulukko", &neliot_taulukko);
}
