// Muuttuva aika-askel: hypyn korkeus riippuu ruudunpäivitysnopeudesta.
#include <print>

struct Hyppy {
    double y = 0.0;   // korkeus metreinä
    double vy = 5.0;  // pystynopeus, m/s
};

// @alku huippu
double huippu(double fps) {
    Hyppy h;
    double korkein = 0.0;
    const double dt = 1.0 / fps;
    while (h.y >= 0.0) {
        h.y += h.vy * dt;   // paikka vanhalla nopeudella
        h.vy -= 9.81 * dt;  // sitten nopeus
        if (h.y > korkein) {
            korkein = h.y;
        }
    }
    return korkein;
}
// @loppu huippu

int main() {
    for (double fps : {20.0, 30.0, 60.0, 144.0}) {
        std::println("{:4.0f} fps: huippu {:.4f} m", fps, huippu(fps));
    }
    std::println("tarkka:   huippu {:.4f} m", 5.0 * 5.0 / (2.0 * 9.81));
}
