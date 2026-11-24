// Kiinteän kokoinen säiepooli: tehtävät jonoon, tulokset futureina.
#pragma once

#include <condition_variable>
#include <cstddef>
#include <functional>
#include <future>
#include <mutex>
#include <queue>
#include <stdexcept>
#include <thread>
#include <type_traits>
#include <utility>
#include <vector>

// @alku luokka
class Saiepooli {
public:
    explicit Saiepooli(std::size_t saikeita)
    {
        if (saikeita == 0) {
            throw std::invalid_argument("saiepooli: 0 saietta");
        }
        for (std::size_t i = 0; i < saikeita; ++i) {
            tyontekijat_.emplace_back([this] { tyoskentele(); });
        }
    }

    Saiepooli(const Saiepooli&) = delete;
    Saiepooli& operator=(const Saiepooli&) = delete;

    // Jonossa olevat tehtävät suoritetaan loppuun ennen purkamista.
    ~Saiepooli()
    {
        {
            std::scoped_lock lukko{mutex_};
            suljettu_ = true;
        }
        herata_.notify_all();
    }   // jthreadit odottavat säikeiden päättymisen tässä

    template <class F>
    auto laheta(F tehtava) -> std::future<std::invoke_result_t<F&>>
    {
        using Tulos = std::invoke_result_t<F&>;
        std::packaged_task<Tulos()> paketti{std::move(tehtava)};
        auto tulos = paketti.get_future();
        {
            std::scoped_lock lukko{mutex_};
            if (suljettu_) {
                throw std::logic_error("saiepooli: suljettu");
            }
            jono_.emplace(std::move(paketti));
        }
        herata_.notify_one();
        return tulos;
    }
// @loppu luokka

// @alku tyoskentele
private:
    void tyoskentele()
    {
        for (;;) {
            std::move_only_function<void()> tehtava;
            {
                std::unique_lock lukko{mutex_};
                herata_.wait(lukko, [this] {
                    return suljettu_ || !jono_.empty();
                });
                if (jono_.empty()) {
                    return;       // suljettu ja jono tyhjä
                }
                tehtava = std::move(jono_.front());
                jono_.pop();
            }
            tehtava();            // lukon ulkopuolella
        }
    }

    std::mutex mutex_;
    std::condition_variable herata_;
    std::queue<std::move_only_function<void()>> jono_;
    bool suljettu_ = false;
    std::vector<std::jthread> tyontekijat_;   // viimeisenä: puretaan
};                                            // ensimmäisenä
// @loppu tyoskentele
