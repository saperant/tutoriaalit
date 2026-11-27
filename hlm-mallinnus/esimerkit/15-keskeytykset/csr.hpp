// Ohjaus- ja tilarekisterien (CSR) numerot ja bitit, jotka malli tuntee.
#pragma once
#include <cstdint>

// @alku csr
// RISC-V:n etuoikeusmäärittelyn konetilan (M) rekistereistä mukana on
// vain keskeytyksen ottamiseen ja siitä palaamiseen tarvittava osa.
namespace csr {
constexpr std::uint32_t mstatus = 0x300;  // tila: MIE ja MPIE
constexpr std::uint32_t mie = 0x304;      // sallitut keskeytyslähteet
constexpr std::uint32_t mtvec = 0x305;    // käsittelijän osoite
constexpr std::uint32_t mepc = 0x341;     // keskeytetyn käskyn osoite
constexpr std::uint32_t mcause = 0x342;   // syy
constexpr std::uint32_t mip = 0x344;      // vireillä olevat (vain luku)

constexpr std::uint32_t MIE = 1u << 3;    // mstatus: keskeytykset sallittu
constexpr std::uint32_t MPIE = 1u << 7;   // mstatus: MIE ennen keskeytystä
constexpr std::uint32_t MTI = 1u << 7;    // mie ja mip: ajastin
constexpr std::uint32_t MEI = 1u << 11;   // mie ja mip: ulkoinen
constexpr std::uint32_t KESKEYTYS = 1u << 31;  // mcause: ylin bitti
}  // namespace csr
// @loppu csr
