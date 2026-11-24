// TSAN
// std::async: käynnistyspolitiikat ja futuren odotus.
#include <atomic>
#include <chrono>
#include <future>
#include <print>
#include <thread>

std::thread::id kuka()
{
    return std::this_thread::get_id();
}

int main()
{
    using namespace std::chrono_literals;
    const auto paasaie = std::this_thread::get_id();

    // @alku politiikat
    // async: uusi säie (tai "kuin uusi säie"), aloittaa heti.
    auto heti = std::async(std::launch::async, kuka);
    // deferred: ei säiettä; funktio ajetaan get()- tai wait()-kutsussa
    // kutsujan säikeessä.
    auto laiska = std::async(std::launch::deferred, kuka);

    std::println("deferred ennen get: {}",
                 laiska.wait_for(0s) == std::future_status::deferred
                     ? "lykatty" : "kaynnissa");
    std::println("async omassa saikeessa: {}",
                 heti.get() != paasaie ? "kylla" : "ei");
    std::println("deferred kutsujan saikeessa: {}",
                 laiska.get() == paasaie ? "kylla" : "ei");
    // @loppu politiikat

    // @alku sudenkuoppa
    // Tulosta ei tallenneta: väliaikaisen futuren hajotin odottaa
    // tehtävän loppuun, joten nämä kaksi ajetaan PERÄKKÄIN.
    std::atomic<int> valmiit{0};
    (void)std::async(std::launch::async, [&] { ++valmiit; });
    const int ensimmaisen_jalkeen = valmiit.load();
    (void)std::async(std::launch::async, [&] { ++valmiit; });
    std::println("ensimmainen valmis ennen toista: {}",
                 ensimmaisen_jalkeen == 1 ? "kylla" : "ei");
    // @loppu sudenkuoppa
}
