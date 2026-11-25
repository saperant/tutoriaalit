#include <array>
#include <print>
#include <span>
#include <vector>

// @alku span
double keskiarvo(std::span<const double> arvot)
{
    double summa = 0;
    for (double x : arvot) {
        summa += x;
    }
    return arvot.empty() ? 0.0 : summa / arvot.size();
}
// @loppu span

int main()
{
    // @alku span-kaytto
    std::vector<double> mittaukset{2.0, 4.0, 9.0};
    std::array<double, 4> kiintea{1.0, 2.0, 3.0, 4.0};
    double c_taulukko[] = {10.0, 20.0};

    std::println("{} {} {}", keskiarvo(mittaukset), keskiarvo(kiintea),
                 keskiarvo(c_taulukko));
    std::println("{}", keskiarvo(std::span{kiintea}.first(2)));
    // @loppu span-kaytto
}
