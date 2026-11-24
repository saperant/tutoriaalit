// Reunojen tunnistus C++:lla: sama ketju kuin Pythonissa, ilman tulkkia.
// Käännös: g++ -std=c++20 reunat.cpp $(pkg-config --cflags --libs opencv4)

#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>

#include <chrono>
#include <cstdio>
#include <cstring>

// @alku kuva
// Synteettinen kuva: kiekkoja ja laatikoita tasaisella pohjalla. Ilman
// satunnaislukuja sama kuva syntyy kaikilla alustoilla ja versioilla.
static cv::Mat synteettinen(int leveys, int korkeus) {
    cv::Mat kuva(korkeus, leveys, CV_8UC1, cv::Scalar(70));
    for (int i = 0; i < 12; ++i) {
        // 4 x 3 -ruudukko, kappale kunkin ruudun keskellä.
        const cv::Point keskus((i % 4) * leveys / 4 + leveys / 8,
                               (i / 4) * korkeus / 3 + korkeus / 6);
        if (i % 2 == 0) {
            cv::circle(kuva, keskus, 15 + i, cv::Scalar(180), cv::FILLED);
        } else {
            cv::rectangle(kuva, keskus - cv::Point(20, 15),
                          keskus + cv::Point(20, 15), cv::Scalar(30),
                          cv::FILLED);
        }
    }
    return kuva;
}
// @loppu kuva

// @alku ketju
struct Tulos {
    int reunapikselit;
    int kayrat;          // yhtenäiset reunakäyrät
};

static Tulos reunat(const cv::Mat& kuva) {
    cv::Mat sumea, reunat;
    cv::GaussianBlur(kuva, sumea, cv::Size(5, 5), 1.2);
    cv::Canny(sumea, reunat, 30, 90);
    cv::Mat nimiot;
    const int alueet = cv::connectedComponents(reunat, nimiot, 8);
    return {cv::countNonZero(reunat), alueet - 1};
}
// @loppu ketju

// @alku paa
int main(int argc, char** argv) {
    cv::setNumThreads(1);                 // toistettava ja reilu mittaus
    const cv::Mat kuva = synteettinen(640, 480);
    const Tulos t = reunat(kuva);
    std::printf("reunapikseleitä %d, reunakäyriä %d\n", t.reunapikselit,
                t.kayrat);
    // Mittaus vain pyydettäessä: ajat vaihtelevat koneittain.
    if (argc > 1 && std::strcmp(argv[1], "--mittaa") == 0) {
        const auto alku = std::chrono::steady_clock::now();
        for (int i = 0; i < 200; ++i) {
            (void)reunat(kuva);
        }
        const std::chrono::duration<double, std::milli> kesto =
            std::chrono::steady_clock::now() - alku;
        std::printf("%.2f ms / kuva\n", kesto.count() / 200.0);
    }
    return 0;
}
// @loppu paa
