// Peliolioiden periytymishierarkia ja sen ongelma: uusi yhdistelmä
// (lentävä ampuja) ei sovi puuhun ilman koodin kopiointia.
#include <memory>
#include <print>
#include <vector>

// @alku hierarkia
class Peliolio {
public:
    virtual ~Peliolio() = default;
    virtual void paivita(double dt) = 0;
    virtual const char* nimi() const = 0;
    double x = 0.0, y = 0.0;
};

class Liikkuva : public Peliolio {
public:
    void paivita(double dt) override { x += vx * dt; }
    double vx = 0.0;
};

class Lentava : public Liikkuva {
public:
    void paivita(double dt) override {
        Liikkuva::paivita(dt);
        y = 2.0;  // leijuu
    }
    const char* nimi() const override { return "lepakko"; }
};

class Ampuja : public Liikkuva {
public:
    void paivita(double dt) override {
        Liikkuva::paivita(dt);
        latausaika -= dt;
        if (latausaika <= 0.0) {
            ++ammuttu;
            latausaika = 1.0;
        }
    }
    const char* nimi() const override { return "tykkimies"; }
    double latausaika = 0.0;
    int ammuttu = 0;
};

// Lentävä ampuja: periä Lentava vai Ampuja? Kumpikin valinta kopioi
// toisen haaran koodin tai johtaa timanttiperintään.
class LentavaAmpuja : public Ampuja {
public:
    void paivita(double dt) override {
        Ampuja::paivita(dt);
        y = 2.0;  // kopioitu Lentava-luokasta
    }
    const char* nimi() const override { return "lentävä ampuja"; }
};
// @loppu hierarkia

int main() {
    std::vector<std::unique_ptr<Peliolio>> oliot;
    oliot.push_back(std::make_unique<Lentava>());
    oliot.push_back(std::make_unique<Ampuja>());
    oliot.push_back(std::make_unique<LentavaAmpuja>());
    for (int i = 0; i < 180; ++i) {
        for (auto& o : oliot) {
            o->paivita(1.0 / 60.0);  // virtuaalikutsu jokaiselle oliolle
        }
    }
    for (const auto& o : oliot) {
        std::println("{:15} y = {:.1f}", o->nimi(), o->y);
    }
}
