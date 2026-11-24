// Ajojen välinen synkronointi: synkronoinnin validointi löytää
// puuttuvat ja liian heikot esteet kahden laskentaajon välillä.
// Kirjoitus ennen lukua (RAW) vaatii muistiesteen, luku ennen
// kirjoitusta (WAR) pelkän suoritusriippuvuuden.
#include "data.hpp"
#include "laskenta.hpp"

#include <algorithm>
#include <string>

struct Vakiot {
    std::uint32_t n;
    float arvo;
};

enum class Este { ei, suoritus, muisti };

// @alku esteet
void tallenna_este(VkCommandBuffer kp, Este e) {
    if (e == Este::suoritus) {
        // Vain järjestys: vaiheet, mutta ei käyttöjä (access mask).
        este(kp, VK_PIPELINE_STAGE_2_COMPUTE_SHADER_BIT, VK_ACCESS_2_NONE,
             VK_PIPELINE_STAGE_2_COMPUTE_SHADER_BIT, VK_ACCESS_2_NONE);
    } else if (e == Este::muisti) {
        laskentaeste(kp);  // järjestys ja kirjoitusten näkyvyys
    }
}
// @loppu esteet

std::string ilmoitukset() {
    std::string s;
    for (const auto& t : Validointi::tunnisteet) {
        if (s.find(t) == std::string::npos) s += (s.empty() ? "" : " ") + t;
    }
    Validointi::tyhjenna();
    return s.empty() ? "ei yhtaan" : s;
}

int main() {
    constexpr std::uint32_t n = 4096;
    VkYmparisto vk(true);  // synkronoinnin validointi päälle
    Puskuri<float> p(vk, n), q(vk, n);
    Putki tayta(vk, "bin/tayta.spv", 1, sizeof(Vakiot));
    Putki saxpy(vk, "bin/saxpy.spv", 2, sizeof(Vakiot));
    const VkDescriptorSet tayta_p = tayta.joukko({p.puskuri});
    const VkDescriptorSet p_q = saxpy.joukko({p.puskuri, q.puskuri});
    const Vakiot v{n, 1.0f};

    std::println("{:24} {:10} {}", "jarjestys", "este", "ilmoitukset");
    const char* esteet[] = {"ei", "suoritus", "muisti"};
    // @alku raw
    // RAW: täyttö kirjoittaa p:n, SAXPY lukee sen (x = p, y = q).
    for (const Este e : {Este::ei, Este::suoritus, Este::muisti}) {
        VkCommandBuffer kp = vk.aloita();
        tayta.aja(kp, tayta_p, v, {ryhmia(n, 256)});
        tallenna_este(kp, e);
        saxpy.aja(kp, p_q, v, {ryhmia(n, 256)});
        vk.suorita(kp);
        // @loppu raw
        std::println("{:24} {:10} {}", "kirjoitus p -> luku p",
                     esteet[static_cast<int>(e)], ilmoitukset());
    }
    // @alku war
    // WAR: SAXPY lukee p:n, sitten täyttö kirjoittaa sen.
    for (const Este e : {Este::ei, Este::suoritus}) {
        VkCommandBuffer kp = vk.aloita();
        saxpy.aja(kp, p_q, v, {ryhmia(n, 256)});
        tallenna_este(kp, e);
        tayta.aja(kp, tayta_p, v, {ryhmia(n, 256)});
        vk.suorita(kp);
        // @loppu war
        std::println("{:24} {:10} {}", "luku p -> kirjoitus p",
                     esteet[static_cast<int>(e)], ilmoitukset());
    }
    return Validointi::raportti();
}
