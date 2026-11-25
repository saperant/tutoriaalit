// GIL kielten rajalla: milloin C++ vapauttaa sen, milloin ottaa sen
// takaisin, ja säikeet C++:n puolella.
#include <pybind11/functional.h>
#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>

#include <atomic>
#include <chrono>
#include <functional>
#include <thread>
#include <vector>

namespace py = pybind11;
using namespace std::chrono_literals;

std::atomic<bool> lippu{false};

// @alku odotus
// Odottaa, että toinen säie asettaa lipun. Jos GIL on varattuna, mikään
// Python-säie ei pääse asettamaan sitä, ja odotus päättyy aikarajaan.
bool odota_lippua(int millisekuntia, bool vapauta)
{
    auto odota = [&] {
        auto raja = std::chrono::steady_clock::now() +
                    std::chrono::milliseconds(millisekuntia);
        while (!lippu.load()) {
            if (std::chrono::steady_clock::now() > raja)
                return false;
            std::this_thread::sleep_for(1ms);
        }
        return true;
    };
    lippu = false;
    if (!vapauta)
        return odota();
    py::gil_scoped_release vapaa;   // GIL palautuu lohkon lopussa
    return odota();
}
// @loppu odotus

// @alku saikeet
// Laskee summan usealla C++-säikeellä. Taulukko luetaan ennen GIL:n
// vapauttamista; vapautuksen jälkeen Python-olioihin ei saa koskea.
double summa_saikeilla(py::array_t<double, py::array::c_style> a,
                       int saikeita)
{
    const double *p = a.data();
    const auto n = static_cast<std::size_t>(a.size());
    std::vector<double> osat(static_cast<std::size_t>(saikeita), 0.0);
    {
        py::gil_scoped_release vapaa;
        std::vector<std::jthread> tyot;
        for (int s = 0; s < saikeita; ++s)
            tyot.emplace_back([&, s] {
                auto i = static_cast<std::size_t>(s);
                auto k = static_cast<std::size_t>(saikeita);
                for (std::size_t j = i * n / k; j < (i + 1) * n / k; ++j)
                    osat[i] += p[j];
            });
    }   // jthread liittyy säikeisiin; sitten GIL otetaan takaisin
    double summa = 0.0;
    for (double o : osat)
        summa += o;
    return summa;
}
// @loppu saikeet

// @alku takaisinkutsu
// C++-säie kutsuu Python-funktiota: sen on otettava GIL ensin.
void raportoi_taustalla(int maara, const std::function<void(int)> &kutsu)
{
    py::gil_scoped_release vapaa;
    std::jthread taustasaie([&] {
        for (int i = 1; i <= maara; ++i) {
            py::gil_scoped_acquire varaa;
            kutsu(i);
        }
    });
}
// @loppu takaisinkutsu

// @alku moduuli
// mod_gil_not_used kertoo vapaasäikeiselle Pythonille (3.13t), että
// moduuli on säieturvallinen ilman GIL:iä. Tavallinen Python ohittaa sen.
PYBIND11_MODULE(rinnakkain, m, py::mod_gil_not_used())
{
    m.def("aseta_lippu", [] { lippu = true; });
    m.def("odota_lippua", &odota_lippua, py::arg("millisekuntia"),
          py::arg("vapauta"));
    m.def("summa_saikeilla", &summa_saikeilla, py::arg("a"),
          py::arg("saikeita"));
    m.def("raportoi_taustalla", &raportoi_taustalla, py::arg("maara"),
          py::arg("kutsu"));
}
// @loppu moduuli
