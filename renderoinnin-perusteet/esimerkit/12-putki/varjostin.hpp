// Varjostinohjelma funktio-oliona: verteksi- ja fragmenttivaihe.
#pragma once
#include "../yhteinen/putki.hpp"
#include "../yhteinen/tekstuuri.hpp"
#include "../yhteinen/valo.hpp"

// @alku yhteiset
// Yhteiset arvot (uniform): samat jokaiselle verteksille ja
// fragmentille yhden piirtokutsun ajan.
struct Yhteiset {
    Mat4 malli, vp;
    Vec3 silma, valo;  // valo: suunta pinnasta valoon
    Vari valon_vari;
};
// @loppu yhteiset

// @alku varjostin
// Vaihtelevat arvot: normaali (3), paikka maailmassa (3), uv (2).
using Vaihtelevat = std::array<double, 8>;

struct Varjostin {
    Yhteiset u;
    Materiaali aine;
    const Mipmap* tekstuuri = nullptr;  // tekstuurin näyte (sampler)

    // Verteksivaihe: mallista leikkausavaruuteen.
    Tulos<8> operator()(const Verteksi& v) const {
        Vec3 p = xyz(u.malli * piste4(v.paikka));
        Vec3 n = muunna_normaali(u.malli, v.normaali);
        return {u.vp * piste4(p),
                {n.x, n.y, n.z, p.x, p.y, p.z, v.uv.x, v.uv.y}};
    }

    // Fragmenttivaihe: pikselin väri interpoloiduista arvoista.
    Vari operator()(const Vaihtelevat& a,
                    const Fragmentti<Vaihtelevat>& f) const {
        Materiaali m = aine;
        if (tekstuuri) {
            double lod = tekstuuri->taso({f.ddx[6], f.ddx[7]},
                                         {f.ddy[6], f.ddy[7]});
            m.diffuusi = m.diffuusi *
                         tekstuuri->trilineaarinen({a[6], a[7]}, lod);
        }
        Vec3 n = normalisoi({a[0], a[1], a[2]});
        Vec3 p{a[3], a[4], a[5]};
        return varjosta(m, n, u.valo, normalisoi(u.silma - p),
                        u.valon_vari);
    }
};
// @loppu varjostin
