// Kokoajan laajennus: CSR-käskyt, mret, wfi ja pino-osoitin.
#pragma once
#include <cstdint>

#include "../14-prototyyppi/rv32.hpp"

namespace rv32 {

// @alku kokoaja
const Rek sp = static_cast<Rek>(2);  // pino-osoitin x2

// SYSTEM-käskyt ovat I-tyyppiä: välittömän arvon paikalla on CSR:n
// numero. Lyhenteet csrw, csrs ja csrr ovat samat kuin oikeassa
// assemblerissa: tulosta tai lähdettä ei tarvita, joten se on x0.
class KeskeytysKokoaja : public Kokoaja {
public:
    void csrrw(Rek rd, std::uint32_t csr, Rek a) { system(1, rd, csr, a); }
    void csrrs(Rek rd, std::uint32_t csr, Rek a) { system(2, rd, csr, a); }
    void csrrc(Rek rd, std::uint32_t csr, Rek a) { system(3, rd, csr, a); }
    void csrw(std::uint32_t csr, Rek a) { csrrw(zero, csr, a); }
    void csrs(std::uint32_t csr, Rek a) { csrrs(zero, csr, a); }
    void csrr(Rek rd, std::uint32_t csr) { csrrs(rd, csr, zero); }
    void mret() { data(0x30200073); }
    void wfi() { data(0x10500073); }

private:
    void system(std::uint32_t f3, Rek rd, std::uint32_t csr, Rek a) {
        data(i_tyyppi(static_cast<std::int32_t>(csr), a, f3, rd, 0x73));
    }
};
// @loppu kokoaja

}  // namespace rv32
