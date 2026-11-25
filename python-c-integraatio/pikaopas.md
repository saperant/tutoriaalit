---
title: Python ja C/C++ yhteen
subtitle: Pikaopas · ctypes, pybind11, nanobind, NumPy, GIL ja pyörät
---

# Valinta

| Tilanne | Väline |
|---------|--------|
| lasku vektoroituu | NumPy, ei käännöstä |
| peräkkäinen silmukka, Python-koodi | Numba (`@njit`) tai Cython |
| valmis C-kirjasto, muutama funktio | `ctypes` |
| laaja C-kirjasto, PyPy | cffi (API-tila) |
| C++-koodi, luokat, poikkeukset | nanobind (uusi), pybind11 (vanha) |
| monta Python-versiota yhdellä pyörällä | nanobind `STABLE_ABI` tai C-API `Py_LIMITED_API` |

Profiloi ensin: `python3 -m cProfile -s tottime ohjelma.py`,
näytteenotto `py-spy` tai `perf` (`python3 -X perf`).

# ctypes

```{.python tiedosto="esimerkit/03-ctypes/main.py" osa="lataus"}
```

- `argtypes` ja `restype` **jokaiselle** funktiolle; `void` →
  `restype = None`.
- Ulostulo: `x = c_double()`, `byref(x)`, `x.value`.
- `errno`: `CDLL(..., use_errno=True)` ja `get_errno()`.
- Kirjaston varaama muisti: `restype = c_void_p`, `string_at`,
  vapautus kirjaston funktiolla `finally`-lohkossa.
- Takaisinkutsu: `CFUNCTYPE(paluu, *argumentit)`; pidä kääre elossa.
  Poikkeus ei ylitä C:tä: palauta virhekoodi.
- NumPy: `a.ctypes.data_as(POINTER(c_double))`, yhtenäinen taulukko.

# C-rajapinta C++:lle

- Läpinäkymätön kahva, `luo`/`tuhoa`-pari, `tuhoa(NULL)` sallittu.
- Paluuarvona tila, tulos ulostuloparametrissa; `virheviesti(tila)`.
- `extern "C"`, `catch (...)` jokaisessa rajafunktiossa.
- `-fvisibility=hidden` ja `__attribute__((visibility("default")))`.
- Versiofunktio; Python-kääre `weakref.finalize` + `with`.

# pybind11

```{.cpp tiedosto="esimerkit/05-pybind11/mittari.cpp" osa="moduuli"}
```

| C++ | Python |
|-----|--------|
| `std::invalid_argument`, `std::domain_error` | `ValueError` |
| `std::out_of_range` | `IndexError` |
| `std::bad_alloc` | `MemoryError` |
| muu `std::exception` | `RuntimeError` |

- `<pybind11/stl.h>`: `vector`↔`list`, `map`↔`dict`,
  `optional`↔`None` – **kopioita**.
- `PYBIND11_MAKE_OPAQUE(T)` + `py::bind_vector<T>`: ei kopiota.
- Tyypit: `.pyi`-tynkä (`pybind11-stubgen`), `py.typed`.

# Elinajat

| Politiikka | Käyttö |
|------------|--------|
| `take_ownership` | osoitin, jonka Python tuhoaa |
| `copy` / `move` | viittaus / arvo (oletus) |
| `reference` | C++ omistaa ja pitää elossa |
| `reference_internal` | viittaus `self`in sisään |

- `py::keep_alive<1, 2>()`: `self` pitää argumentin elossa.
- `py::class_<T, std::shared_ptr<T>>` tai `py::classh<T>` jaettuun
  omistukseen.
- Testaa: staattinen elossa-laskuri, AddressSanitizer.

# nanobind

| pybind11 | nanobind |
|----------|----------|
| `PYBIND11_MODULE` | `NB_MODULE` |
| `py::` | `nb::` |
| `def_property_readonly` | `def_prop_ro` |
| `register_exception` | `nb::exception` |
| `<pybind11/stl.h>` | `<nanobind/stl/vector.h>` jne. |
| `return_value_policy` | `rv_policy` |
| `py::array_t` | `nb::ndarray` |

Ydin `libnanobind` käännetään kerran (`nanobind_add_module`). Ei
moniperintää; vuodot raportoidaan tulkin sulkeutuessa.

# NumPy ilman kopiota

```{.cpp tiedosto="esimerkit/08-numpy/kuva.cpp" osa="kynnys"}
```

- Muokkaava funktio: tarkka tyyppi ja `py::arg("a").noconvert()`.
- Lukeva: `py::array_t<T, py::array::c_style | py::array::forcecast>`.
- `unchecked<N>()` noudattaa askeleita, ei rajatarkistuksia.
- Uusi tulos: `py::array_t<T> y({h, w})`, täytä `mutable_unchecked`.
- C++:n muisti: `py::array_t<T>(muoto, askeleet, ptr, base)`.
- nanobind: `nb::ndarray<const float, nb::ndim<1>, nb::c_contig,
  nb::device::cpu>`; DLPack (PyTorch, JAX, CuPy).
- Oletustyypit: `np.array([1.0])` on `float64`, `[1]` on `int64`.

# GIL

```{.cpp tiedosto="esimerkit/10-gil/rinnakkain.cpp" osa="takaisinkutsu"}
```

- `py::gil_scoped_release`: pitkä lasku, I/O, odotus. **Ei
  Python-olioita** lohkossa.
- `py::gil_scoped_acquire`: C++-säie kutsuu Pythonia.
- Älä odota lukko varattuna säiettä, joka tarvitsee lukkoa.
- Vapaasäikeinen 3.13t/3.14t: `py::mod_gil_not_used()`, nanobind
  `FREE_THREADED`; globaali tila itse suojattuna.

# C-API

| Viite | Merkitys | Esimerkki |
|-------|----------|-----------|
| uusi | omistat, `Py_DECREF` | `PyObject_GetIter`, `PyFloat_FromDouble` |
| lainattu | et omista | `PyList_GET_ITEM`, argumentit |

- Paluuarvo aina uusi viite: `Py_NewRef(lainattu)`.
- Virhe: aseta (`PyErr_SetString`), siivoa, palauta `NULL`.
- `-1.0` / `NULL` epäselvä: `PyErr_Occurred()`.
- Testi: `sys.getrefcount` ennen ja jälkeen silmukan.

# Kutsun hinta

- Kutsu ≈ 50–300 ns; `x * x` Pythonissa on halvempi.
- Lista → `std::vector` muuntaa alkiot; taulukko ei.
- Silmukka C++:aan, rajapinta erille, tila C++-olioon.
- Mittaa: paras usean ajon ajasta, `-O2`, `timeit`.

# Pyörät

```{.toml tiedosto="esimerkit/12-paketointi/pyproject.toml" osa="projekti"}
```

| Tunniste | Merkitys |
|----------|----------|
| `cp312-cp312` | CPython 3.12 |
| `cp312-abi3` | 3.12 ja uudemmat (vakaa ABI) |
| `cp313t` | vapaasäikeinen 3.13 |
| `manylinux_2_28_x86_64` | glibc ≥ 2.28 |
| `linux_x86_64` | vain rakennuskone, ei PyPI:hin |

```text
python3 -m build                 # sdist ja pyörä
auditwheel repair dist/*.whl     # manylinux-tunniste ja kirjastot
cibuildwheel --platform linux    # kaikki versiot CI:ssä
```

Testaa asennettua pyörää, älä lähdehakemistoa.
