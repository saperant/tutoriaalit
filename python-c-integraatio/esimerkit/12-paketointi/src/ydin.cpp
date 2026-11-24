// CRC-32 mille tahansa puskuriprotokollaa tukevalle oliolle (bytes,
// bytearray, memoryview, NumPy-taulukko) ilman kopiointia.
#include <pybind11/pybind11.h>

#include <cstdint>
#include <stdexcept>

namespace py = pybind11;

// @alku crc
std::uint32_t crc32(const py::buffer &puskuri)
{
    py::buffer_info tiedot = puskuri.request();      // ei kopiota
    if (tiedot.ndim != 1 || tiedot.strides[0] != tiedot.itemsize)
        throw std::invalid_argument("odotettiin yhtenäinen puskuri");
    const auto *p = static_cast<const std::uint8_t *>(tiedot.ptr);
    const auto n = static_cast<std::size_t>(tiedot.size * tiedot.itemsize);
    std::uint32_t crc = 0xFFFFFFFFu;
    {
        py::gil_scoped_release vapaa;   // puskuri pysyy lukittuna
        for (std::size_t i = 0; i < n; ++i) {
            crc ^= p[i];
            for (int b = 0; b < 8; ++b)
                crc = (crc >> 1) ^ (0xEDB88320u & (0u - (crc & 1u)));
        }
    }
    return ~crc;
}

PYBIND11_MODULE(_ydin, m)
{
    m.def("crc32", &crc32, py::arg("puskuri"));
}
// @loppu crc
