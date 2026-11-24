// NumPy-taulukot pybind11:llä ilman kopiointia: puskuriprotokolla,
// askeleet (strides), tietotyypin tarkistus ja jaettu muisti.
#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>

#include <cstdint>
#include <stdexcept>
#include <vector>

namespace py = pybind11;

// @alku kynnys
// Muokkaa kuvaa paikallaan. unchecked-näkymä noudattaa askeleita, joten
// myös viipale (esim. kuva[:, ::2]) käsitellään ilman kopiota.
void kynnysta(py::array_t<std::uint8_t> kuva, std::uint8_t raja)
{
    auto k = kuva.mutable_unchecked<2>();   // ei tarkistuksia silmukassa
    for (py::ssize_t y = 0; y < k.shape(0); ++y)
        for (py::ssize_t x = 0; x < k.shape(1); ++x)
            k(y, x) = k(y, x) >= raja ? 255 : 0;
}
// @loppu kynnys

// @alku sumennus
// Palauttaa uuden taulukon. Syöte saa olla mitä tahansa tyyppiä:
// forcecast muuntaa sen float32:ksi ja c_style yhtenäiseksi (kopio).
py::array_t<float> sumenna(
    py::array_t<float, py::array::c_style | py::array::forcecast> kuva)
{
    if (kuva.ndim() != 2)
        throw std::invalid_argument("odotettiin 2-ulotteinen kuva");
    const py::ssize_t h = kuva.shape(0), w = kuva.shape(1);
    py::array_t<float> tulos({h, w});
    auto s = kuva.unchecked<2>();
    auto t = tulos.mutable_unchecked<2>();
    for (py::ssize_t y = 0; y < h; ++y)
        for (py::ssize_t x = 0; x < w; ++x) {
            float summa = 0.0f;
            int n = 0;
            for (py::ssize_t dy = -1; dy <= 1; ++dy)
                for (py::ssize_t dx = -1; dx <= 1; ++dx) {
                    py::ssize_t yy = y + dy, xx = x + dx;
                    if (yy >= 0 && yy < h && xx >= 0 && xx < w) {
                        summa += s(yy, xx);
                        ++n;
                    }
                }
            t(y, x) = summa / static_cast<float>(n);
        }
    return tulos;
}
// @loppu sumennus

// @alku puskuri
// C++-olio omistaa muistin; taulukko() antaa siihen näkymän, joka
// pitää olion elossa (base-olio).
class Kehys {
public:
    Kehys(py::ssize_t h, py::ssize_t w)
        : h_(h), w_(w), data_(static_cast<std::size_t>(h * w), 0) {}

    py::array_t<std::uint8_t> taulukko(const py::object &itse)
    {
        return py::array_t<std::uint8_t>(
            {h_, w_},                                   // muoto
            {w_ * py::ssize_t{1}, py::ssize_t{1}},      // askeleet tavuina
            data_.data(), itse);                        // ei kopiota
    }

    long summa() const
    {
        long s = 0;
        for (auto v : data_)
            s += v;
        return s;
    }

private:
    py::ssize_t h_, w_;
    std::vector<std::uint8_t> data_;
};
// @loppu puskuri

PYBIND11_MODULE(kuva, m)
{
    // @alku sidonta
    // noconvert: väärä tietotyyppi on virhe, ei hiljainen kopio, jonka
    // muutokset katoaisivat.
    m.def("kynnysta", &kynnysta, py::arg("kuva").noconvert(),
          py::arg("raja"));
    m.def("sumenna", &sumenna, py::arg("kuva"));
    py::class_<Kehys>(m, "Kehys")
        .def(py::init<py::ssize_t, py::ssize_t>())
        .def("taulukko", [](py::object itse) {
            return itse.cast<Kehys &>().taulukko(itse);
        })
        .def("summa", &Kehys::summa);
    // @loppu sidonta
}
