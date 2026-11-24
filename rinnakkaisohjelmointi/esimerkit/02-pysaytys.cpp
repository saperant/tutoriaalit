// TSAN
// Pysäytyspyyntö: std::jthread, std::stop_token, std::stop_callback ja
// ehtomuuttujan odotus, joka herää myös pysäytyspyyntöön.
#include <condition_variable>
#include <deque>
#include <mutex>
#include <print>
#include <stop_token>
#include <string>
#include <thread>
#include <vector>

// @alku tyontekija
class Kasittelija {
public:
    void lisaa(std::string tyo)
    {
        {
            std::scoped_lock lukko{mutex_};
            jono_.push_back(std::move(tyo));
        }
        uusi_tyo_.notify_one();
    }

    // Käsittelee töitä, kunnes pysäytystä pyydetään. Odotus herää sekä
    // uuteen työhön että pysäytyspyyntöön.
    void aja(std::stop_token pysayta)
    {
        std::unique_lock lukko{mutex_};
        for (;;) {
            const bool tyota = uusi_tyo_.wait(lukko, pysayta, [this] {
                return !jono_.empty();
            });
            if (!tyota) {
                return;   // pysäytys pyydetty eikä töitä ole jäljellä
            }
            std::string tyo = std::move(jono_.front());
            jono_.pop_front();
            lukko.unlock();
            kasitellyt_.push_back(tyo.size());  // vain tämä säie
            lukko.lock();
        }
    }

    const std::vector<std::size_t>& kasitellyt() const
    {
        return kasitellyt_;
    }

private:
    std::mutex mutex_;
    std::condition_variable_any uusi_tyo_;   // _any: tukee stop_tokenia
    std::deque<std::string> jono_;
    std::vector<std::size_t> kasitellyt_;
};
// @loppu tyontekija

int main()
{
    // @alku kaytto
    Kasittelija kasittelija;
    bool ilmoitettu = false;
    {
        std::jthread saie{[&kasittelija](std::stop_token t) {
            kasittelija.aja(t);
        }};
        // Takaisinkutsu ajetaan request_stop()-kutsun aikana pyytäjän
        // säikeessä (tai heti, jos pysäytys on jo pyydetty).
        std::stop_callback ilmoitus{saie.get_stop_token(),
                                    [&ilmoitettu] { ilmoitettu = true; }};
        for (const char* tyo : {"a", "bb", "ccc"}) {
            kasittelija.lisaa(tyo);
        }
        saie.request_stop();   // ennen kuin ilmoitus puretaan
    }   // jthreadin hajotin odottaa säikeen
    // @loppu kaytto
    std::println("takaisinkutsu ajettu: {}", ilmoitettu ? "kylla" : "ei");
    const auto& k = kasittelija.kasitellyt();
    std::println("kasitelty {} tyota, pituudet {} {} {}", k.size(), k.at(0),
                 k.at(1), k.at(2));
}
