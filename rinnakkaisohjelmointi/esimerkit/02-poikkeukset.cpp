// TSAN
// Poikkeus säikeestä kutsujalle: std::exception_ptr, std::promise ja
// std::packaged_task.
#include <exception>
#include <future>
#include <print>
#include <stdexcept>
#include <string>
#include <thread>
#include <utility>

int jasenna(const std::string& teksti)
{
    std::size_t kaytetty = 0;
    const int arvo = std::stoi(teksti, &kaytetty);
    if (kaytetty != teksti.size()) {
        throw std::invalid_argument("roskaa luvun perassa: " + teksti);
    }
    return arvo;
}

int main()
{
    // @alku exception-ptr
    std::exception_ptr virhe;
    {
        std::jthread saie{[&virhe] {
            try {
                (void)jasenna("12x");
            } catch (...) {
                virhe = std::current_exception();  // talteen
            }
        }};
    }
    try {
        if (virhe) {
            std::rethrow_exception(virhe);
        }
    } catch (const std::invalid_argument& e) {
        std::println("saikeen virhe: {}", e.what());
    }
    // @loppu exception-ptr

    // @alku promise
    std::promise<int> lupaus;
    std::future<int> tulos = lupaus.get_future();
    std::jthread tuottaja{[p = std::move(lupaus)]() mutable {
        try {
            p.set_value(jasenna("42"));
        } catch (...) {
            p.set_exception(std::current_exception());
        }
    }};
    std::println("promise: {}", tulos.get());   // odottaa arvoa
    // @loppu promise

    // @alku paketti
    std::packaged_task<int(const std::string&)> tehtava{jasenna};
    std::future<int> tulos2 = tehtava.get_future();
    {
        std::jthread suorittaja{std::move(tehtava), std::string{"7kg"}};
    }   // säie ja sen tehtäväkopio on purettu ennen käsittelyä (luku 11)
    try {
        std::println("packaged_task: {}", tulos2.get());
    } catch (const std::exception& e) {
        std::println("packaged_task: virhe: {}", e.what());
    }
    // @loppu paketti
}
