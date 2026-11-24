// Virta C-simulaatiota varten: jono, jonka luku tyhjästä on virhe.
// Laitteistossa vastaa AXI-Streamia (TDATA, TVALID, TREADY).
#pragma once
#include <cstdio>
#include <cstdlib>
#include <deque>
#include <vector>

template <typename T>
class virta {
public:
    // @alku virta
    T read() {
        if (jono_.empty()) {
            std::fputs("virta: luku tyhjästä virrasta\n", stderr);
            std::abort();
        }
        T arvo = jono_.front();
        jono_.pop_front();
        return arvo;
    }
    void write(const T& arvo) { jono_.push_back(arvo); }
    // @loppu virta
    bool empty() const { return jono_.empty(); }
    std::vector<T> tyhjenna() {
        std::vector<T> tulos(jono_.begin(), jono_.end());
        jono_.clear();
        return tulos;
    }

private:
    std::deque<T> jono_;
};
