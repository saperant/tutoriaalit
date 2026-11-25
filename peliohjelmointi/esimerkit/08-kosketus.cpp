// Lepäävät kosketukset: kappale, joka makaa lattialla tai toisen
// päällä, törmää siihen joka askeleella. Kaksi ongelmaa ja niiden
// korjaukset: loputon pomppiminen (lepokynnys) ja pinon vajoaminen
// (rajoitteiden iterointi ja sijainnin korjaus).
#include <array>
#include <print>

constexpr double DT = 1.0 / 60.0;
constexpr double G = 10.0;  // m/s² alaspäin; y kasvaa ylöspäin

// @alku kynnys
// Pallo putoaa lattialle. Kimmokerroin 0,5 puolittaa nopeuden joka
// pompulla, mutta painovoima antaa joka askeleella uutta nopeutta, joten
// pallo ei koskaan pysähdy. Lepokynnys: hidas osuma ei kimmoa.
struct Pomppu {
    int pomppuja;
    bool levossa;
};

Pomppu pudota(double lepokynnys) {
    double y = 2.0, v = 0.0;
    int pomppuja = 0;
    bool levossa = false;
    for (int i = 0; i < 600; ++i) {  // 10 s
        v -= G * DT;
        y += v * DT;
        if (y < 0.0) {
            y = 0.0;
            if (-v < lepokynnys) {
                v = 0.0;
                levossa = true;
            } else {
                v = -0.5 * v;
                ++pomppuja;
                levossa = false;
            }
        }
    }
    return {pomppuja, levossa};
}
// @loppu kynnys

// @alku pino
// Neljä metrin laatikkoa päällekkäin. Kosketukset (lattia–1, 1–2, 2–3,
// 3–4) ratkaistaan yksi kerrallaan: jos kappaleet lähestyvät, niiden
// nopeudet tasataan. Yhden kosketuksen korjaus rikkoo naapurin, joten
// kierroksia tarvitaan useita.
constexpr int N = 4;

struct Pino {
    std::array<double, N> y{}, v{};
};

void ratkaise_nopeudet(Pino& p, int kierroksia) {
    for (int k = 0; k < kierroksia; ++k) {
        if (p.v[0] < 0.0) {
            p.v[0] = 0.0;  // lattia ei liiku
        }
        for (int i = 1; i < N; ++i) {
            if (p.v[i] < p.v[i - 1]) {  // ylempi lähestyy alempaa
                const double keski = 0.5 * (p.v[i] + p.v[i - 1]);
                p.v[i] = p.v[i - 1] = keski;  // samat massat, e = 0
            }
        }
    }
}

// Sijainnin korjaus: nopeuksien ratkaisu ei poista jo syntynyttä
// limitystä. Limityksestä korjataan osa (20 %) joka askeleella, ja
// pieni sallittu vara estää värinän.
void korjaa_sijainnit(Pino& p) {
    constexpr double OSUUS = 0.2, VARA = 0.005;
    double alla = 0.0;  // alemman kappaleen yläpinta
    for (int i = 0; i < N; ++i) {
        const double limitys = alla - (p.y[i] - 0.5);
        if (limitys > VARA) {
            p.y[i] += OSUUS * (limitys - VARA);
        }
        alla = p.y[i] + 0.5;
    }
}

// Palauttaa ylimmän laatikon vajoaman kahden sekunnin jälkeen.
double simuloi(int kierroksia, bool korjaus) {
    Pino p;
    for (int i = 0; i < N; ++i) {
        p.y[i] = 0.5 + i;  // laatikot täsmälleen päällekkäin
    }
    for (int askel = 0; askel < 120; ++askel) {
        for (int i = 0; i < N; ++i) {
            p.v[i] -= G * DT;
        }
        ratkaise_nopeudet(p, kierroksia);
        for (int i = 0; i < N; ++i) {
            p.y[i] += p.v[i] * DT;
        }
        if (korjaus) {
            korjaa_sijainnit(p);
        }
    }
    return (0.5 + (N - 1)) - p.y[N - 1];
}
// @loppu pino

int main() {
    for (double kynnys : {0.0, 0.5}) {
        const Pomppu p = pudota(kynnys);
        std::println("lepokynnys {:.1f} m/s: {:3} pomppua 10 s:ssa, "
                     "levossa: {}", kynnys, p.pomppuja, p.levossa);
    }
    std::println("neljän laatikon pino, ylimmän vajoama 2 s:n jälkeen:");
    for (int kierroksia : {1, 2, 4, 8, 16}) {
        std::println("  {:2} kierrosta: {:6.3f} m, sijainnin korjauksella "
                     "{:6.3f} m", kierroksia, simuloi(kierroksia, false),
                     simuloi(kierroksia, true));
    }
}
