#include <print>
#include <string>

int main()
{
    std::string kieli = "C++";
    int versio = 23;
    std::println("Hei, moderni {}!", kieli);
    std::println("Käytössä on {}{}.", kieli, versio);
}
