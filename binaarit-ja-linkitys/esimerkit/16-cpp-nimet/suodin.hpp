#ifndef SUODIN_HPP
#define SUODIN_HPP
// @alku otsake
// Otsake kelpaa sekä C:lle että C++:lle: C++ näkee extern "C" -lohkon.
#ifdef __cplusplus
extern "C" {
#endif

double suodin_keskiarvo(const double *arvot, int n);

#ifdef __cplusplus
}
#endif
// @loppu otsake
#endif
