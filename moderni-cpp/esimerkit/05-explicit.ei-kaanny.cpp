#include <print>

class Metrit {
public:
    explicit Metrit(double arvo) : arvo_{arvo} {}
    double arvo() const { return arvo_; }

private:
    double arvo_;
};

void tulosta(Metrit m)
{
    std::println("{} m", m.arvo());
}

int main()
{
    tulosta(Metrit{2.5});   // selvä tarkoitus: sallittu
#ifndef KORJATTU
    tulosta(2.5);           // virhe: double ei muunnu Metreiksi
#endif
}
