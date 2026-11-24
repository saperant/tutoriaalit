// TSAN
// Kertaalustus: std::call_once ja funktion paikallinen static.
#include <atomic>
#include <map>
#include <mutex>
#include <print>
#include <string>
#include <thread>
#include <vector>

std::atomic<int> alustuksia{0};

// @alku kerran
class Sanakirja {
public:
    const std::string& kaanna(const std::string& sana)
    {
        std::call_once(lippu_, [this] { lataa(); });  // vain kerran
        return sanat_.at(sana);          // luku alustuksen jälkeen
    }

private:
    void lataa()
    {
        ++alustuksia;
        sanat_ = {{"thread", "saie"}, {"lock", "lukko"}};
    }

    std::once_flag lippu_;
    std::map<std::string, std::string> sanat_;
};
// @loppu kerran

// @alku static
// C++11:stä alkaen funktion paikallisen staticin alustus on
// säieturvallinen: kääntäjä tuottaa saman kertaalustuksen.
Sanakirja& sanakirja()
{
    static Sanakirja ainoa;
    return ainoa;
}
// @loppu static

int main()
{
    std::vector<std::string> tulokset(6);
    {
        std::vector<std::jthread> saikeet;
        for (std::size_t s = 0; s < tulokset.size(); ++s) {
            saikeet.emplace_back([&tulokset, s] {
                tulokset[s] = sanakirja().kaanna(s % 2 ? "lock" : "thread");
            });
        }
    }
    std::println("alustuksia {}", alustuksia.load());
    std::println("{} {} {}", tulokset[0], tulokset[1], tulokset[5]);
}
