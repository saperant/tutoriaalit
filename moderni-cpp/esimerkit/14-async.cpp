// TSAN
#include <future>
#include <print>
#include <stdexcept>

// @alku funktiot
long long fibonacci(int n)
{
    if (n < 0) {
        throw std::invalid_argument{"negatiivinen syöte"};
    }
    return n < 2 ? n : fibonacci(n - 1) + fibonacci(n - 2);
}
// @loppu funktiot

int main()
{
    // @alku async
    auto a = std::async(std::launch::async, fibonacci, 30);
    auto b = std::async(std::launch::async, fibonacci, 25);
    std::println("fib(30) + fib(25) = {}", a.get() + b.get());

    auto virheellinen = std::async(std::launch::async, fibonacci, -1);
    try {
        virheellinen.get();   // säikeen poikkeus heitetään uudelleen
    } catch (const std::exception& e) {
        std::println("virhe säikeessä: {}", e.what());
    }
    // @loppu async
}
