#include <print>
#include <string>

// @alku luokat
class Tili {
public:
    virtual ~Tili() = default;
    virtual std::string kuvaus() const { return "tili"; }
};

class Saastotili : public Tili {
public:
    std::string kuvaus() const override { return "säästötili, korko 2 %"; }
};
// @loppu luokat

// @alku kaytto
void arvona(Tili t)
{
    std::println("arvona:    {}", t.kuvaus());
}

void viittauksena(const Tili& t)
{
    std::println("viittaus:  {}", t.kuvaus());
}

int main()
{
    Saastotili s;
    arvona(s);         // kopioidaan vain Tili-osa: olio viipaloituu
    viittauksena(s);   // dynaaminen sidonta toimii
}
// @loppu kaytto
