// Q1.15-aritmetiikka: pyoristys ja saturaatio.
#pragma once
#include <stdint.h>

// @alku q15
static inline int16_t q15_saturoi(int64_t v)
{
    return (int16_t)(v > INT16_MAX ? INT16_MAX
                     : v < INT16_MIN ? INT16_MIN : v);
}

// Q.30-kertyma -> Q1.15: pyoristys lahimpaan (puolikas ylospain).
// Negatiivisen luvun >> on GCC:ssa ja Clangissa aritmeettinen siirto.
static inline int64_t q15_pyorista(int64_t kertyma)
{
    return (kertyma + (1 << 14)) >> 15;
}
// @loppu q15
