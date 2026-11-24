// Käännösaikainen laskenta: CRC-32-taulukko lasketaan käännöksessä.
#include <array>
#include <cstdint>
#include <cstdio>
#include <string>
#include <string_view>

// @alku taulukko
// consteval: funktio on pakko suorittaa käännösaikana. Valmis ohjelma
// sisältää vain taulukon, ei sen laskevaa koodia.
consteval std::array<std::uint32_t, 256> tee_taulukko()
{
    std::array<std::uint32_t, 256> t{};
    for (std::uint32_t i = 0; i < 256; ++i) {
        std::uint32_t c = i;
        for (int k = 0; k < 8; ++k) {
            c = (c & 1) ? 0xEDB88320u ^ (c >> 1) : c >> 1;
        }
        t[i] = c;
    }
    return t;
}

constexpr auto crc_taulukko = tee_taulukko();

// constexpr: toimii sekä käännösaikana että ajon aikana.
constexpr std::uint32_t crc32(std::string_view data)
{
    std::uint32_t c = 0xFFFFFFFFu;
    for (char merkki : data) {
        auto tavu = static_cast<unsigned char>(merkki);
        c = crc_taulukko[(c ^ tavu) & 0xFF] ^ (c >> 8);
    }
    return c ^ 0xFFFFFFFFu;
}

// Tarkistus käännösaikana: standardin tarkistusarvo.
static_assert(crc32("123456789") == 0xCBF43926u);
// @loppu taulukko

int main(int argc, char** argv)
{
    // @alku ajonaikainen
    std::string viesti = "CRC lasketaan ajon aikana";
    for (int i = 1; i < argc; ++i) {
        viesti += argv[i];
    }
    std::printf("crc32(\"%s\") = %08X\n", viesti.c_str(), crc32(viesti));
    constexpr std::uint32_t vakio = crc32("vakio");   // käännösaikana
    std::printf("crc32(\"vakio\") = %08X\n", vakio);
    // @loppu ajonaikainen
}
