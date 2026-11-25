// TSAN
#include <chrono>
#include <latch>
#include <print>
#include <stop_token>
#include <thread>

int main()
{
    // @alku pysaytys
    using namespace std::chrono_literals;
    std::latch kaynnissa{1};

    std::jthread tyontekija([&kaynnissa](std::stop_token pysayta) {
        std::println("työntekijä aloitti");
        kaynnissa.count_down();
        while (!pysayta.stop_requested()) {
            std::this_thread::sleep_for(1ms);   // "työtä"
        }
        std::println("työntekijä lopetti");
    });

    kaynnissa.wait();             // odotetaan, että säie on käynnissä
    tyontekija.request_stop();    // pyydetään lopettamaan
    tyontekija.join();
    std::println("pääsäie jatkaa");
    // @loppu pysaytys
}
