#include <print>
#include <vector>

int main()
{
    std::vector<int> jono{10, 20, 30};
    const int& ensimmainen = jono[0];   // viittaus vektorin muistiin
    jono.push_back(40);                 // kapasiteetti loppuu: muisti
                                        // varataan uudelleen
    std::println("{}", ensimmainen);    // viittaa vapautettuun muistiin
}
