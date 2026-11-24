// Whitted-säteenseuranta: varjot, peiliheijastus ja taittuminen.
#include <cstdio>

#include "yhteinen/kamera.hpp"
#include "yhteinen/kuva.hpp"
#include "yhteinen/materiaali.hpp"

const int L = 64, K = 48;

// @alku kohtaus
struct Esine {
    Pallo pallo;
    Materiaali m;
};
const Esine ESINEET[] = {
    {{{-1.0, 0.5, 0.4}, 0.5}, {.laji = Materiaali::peili,
                               .vari = {0.9, 0.9, 0.9}}},
    {{{0.15, 0.45, -0.5}, 0.45}, {.laji = Materiaali::lasi,
                                  .vari = {1, 1, 1}}},
    {{{1.1, 0.4, 0.5}, 0.4}, {.vari = {0.7, 0.12, 0.08}}},
};
const Vec3 VALO{-2, 4, -3};                 // pistevalo
const double VALO_I = 40;                   // intensiteetti
const double SIIRTO_W = 1e-7;               // ks. luku Leikkaukset
// @loppu kohtaus

struct Laskurit {
    long ensisijaiset = 0, varjot = 0, heijastukset = 0, taittumiset = 0;
    long kokonaisheijastukset = 0;
} laskurit;

struct Osuma {
    double t = AARETON;
    Vec3 p, n;
    Materiaali m;
};

Osuma leikkaa(const Sade& s, double tmax = AARETON) {
    Osuma o;
    o.t = tmax;
    for (const Esine& e : ESINEET) {
        double t = leikkaa_pallo(e.pallo, s, 0, o.t);
        if (t < o.t) {
            o = {t, kohta(s, t), normalisoi(kohta(s, t) - e.pallo.keski),
                 e.m};
        }
    }
    double t = leikkaa_taso({{0, 1, 0}, 0}, s, 0, o.t);
    if (t < o.t) {                               // shakkilauta
        Vec3 p = kohta(s, t);
        bool ruutu = (static_cast<int>(std::floor(p.x)) +
                      static_cast<int>(std::floor(p.z))) % 2 != 0;
        double v = ruutu ? 0.7 : 0.15;
        o = {t, p, {0, 1, 0}, {.vari = {v, v, v}}};
    }
    if (o.t == tmax) o.t = AARETON;
    return o;
}

// @alku jalita
Vari jaljita(const Sade& s, int syvyys) {
    Osuma o = leikkaa(s);
    if (o.t == AARETON) {                         // taivas
        double y = std::max(0.0, s.d.y);
        return {0.3 + 0.2 * y, 0.45 + 0.25 * y, 0.7 + 0.3 * y};
    }
    if (syvyys == 0) return {};
    bool ulkoa = piste(o.n, s.d) < 0;
    Vec3 n = ulkoa ? o.n : -o.n;                  // tulopuolen normaali
    if (o.m.laji == Materiaali::peili) {
        ++laskurit.heijastukset;
        Sade r{o.p + SIIRTO_W * n, heijasta(s.d, n)};
        return o.m.vari * jaljita(r, syvyys - 1);
    }
    if (o.m.laji == Materiaali::lasi) {
        double eta = ulkoa ? 1 / o.m.taitekerroin : o.m.taitekerroin;
        double F = fresnel(-piste(s.d, n), eta);
        ++laskurit.heijastukset;
        Vari tulos = F * jaljita({o.p + SIIRTO_W * n, heijasta(s.d, n)},
                                 syvyys - 1);
        if (auto t = taita(s.d, n, eta)) {
            ++laskurit.taittumiset;
            tulos = tulos + (1 - F) * jaljita({o.p - SIIRTO_W * n,
                                               normalisoi(*t)},
                                              syvyys - 1);
        } else {
            ++laskurit.kokonaisheijastukset;
        }
        return tulos;
    }
    // Diffuusi pinta: Lambert pistevalosta, jos varjosäde pääsee perille.
    Vec3 p = o.p + SIIRTO_W * n;
    Vec3 l = VALO - p;
    double r2 = piste(l, l);
    l = (1 / std::sqrt(r2)) * l;
    Vari ymparisto = 0.03 * o.m.vari;
    double c = piste(n, l);
    if (c <= 0) return ymparisto;
    ++laskurit.varjot;
    if (leikkaa({p, l}, std::sqrt(r2)).t < AARETON) return ymparisto;
    return ymparisto + (VALO_I * c / (PII * r2)) * o.m.vari;
}
// @loppu jalita

int main() {
    // @alku main
    Kamera k = kamera({0.3, 1.3, -3.4}, {0, 0.45, 0}, {0, 1, 0}, 1.7, L, K);
    Kehys kuva(L, K);
    for (int y = 0; y < K; ++y)
        for (int x = 0; x < L; ++x) {
            Vari summa{};
            for (double dy : {0.25, 0.75})          // 2 x 2 näytettä
                for (double dx : {0.25, 0.75}) {
                    ++laskurit.ensisijaiset;
                    summa = summa + jaljita(k.sade(x + dx, y + dy), 6);
                }
            kuva(x, y) = 0.25 * summa;
        }
    raportti("Whitted", kuva);
    std::printf("säteitä: ensisijaisia %ld, varjo %ld, heijastus %ld,\n"
                "         taittuminen %ld, kokonaisheijastus %ld\n",
                laskurit.ensisijaiset, laskurit.varjot,
                laskurit.heijastukset, laskurit.taittumiset,
                laskurit.kokonaisheijastukset);
    ascii(kuva, 2, 4);
    tallenna_ppm(kuva, "05-whitted.ppm");
    // @loppu main
}
