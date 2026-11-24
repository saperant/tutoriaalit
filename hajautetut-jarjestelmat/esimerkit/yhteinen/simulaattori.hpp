// Deterministinen verkkosimulaattori.
//
// Solmut ovat tilakoneita, jotka reagoivat viesteihin ja ajastimiin.
// Simulaattori pitää tapahtumajonoa simuloidussa ajassa ja päättää
// siemenestä, kuinka kauan kukin viesti kulkee, katoaako se ja
// monistuuko se. Testi voi lisäksi jakaa verkon osiin, kaataa solmuja
// ja käynnistää ne uudelleen. Kaikki tapahtuu yhdessä säikeessä, joten
// sama siemen tuottaa aina saman suorituksen.
#pragma once
#include <cstdint>
#include <cstdio>
#include <functional>
#include <memory>
#include <optional>
#include <queue>
#include <string>
#include <utility>
#include <vector>

#include "satunnainen.hpp"

using Aika = std::int64_t;  // simuloitu aika millisekunteina

// @alku rajapinta
// Se osa maailmasta, jonka solmu näkee: oma tunniste, paikallinen
// kello, viestien lähetys, ajastimet ja oma satunnaislukuvirta.
template <class V>
class Yhteys {
public:
    virtual ~Yhteys() = default;
    virtual int oma() const = 0;
    virtual int solmuja() const = 0;
    virtual Aika kello() const = 0;          // paikallinen, ajautuu
    virtual void laheta(int kohde, V viesti) = 0;
    virtual void ajasta(Aika viive, int tunniste) = 0;
    virtual Satunnainen& satunnainen() = 0;
    virtual void kirjaa(const std::string& rivi) = 0;
};

// Solmu on tilakone. Kaikki tila, joka ei ole pysyvää, katoaa
// kaatuessa, koska simulaattori tuhoaa olion.
template <class V>
class Solmu {
public:
    virtual ~Solmu() = default;
    virtual void kaynnisty(Yhteys<V>&) {}
    virtual void vastaanota(Yhteys<V>&, int lahettaja, const V&) = 0;
    virtual void ajastin(Yhteys<V>&, int) {}
};
// @loppu rajapinta

// @alku asetukset
struct Verkkoasetukset {
    Aika viive_min = 1;    // viestin kulkuaika ms
    Aika viive_max = 10;
    int katoaa = 0;        // promillea viesteistä katoaa
    int monistuu = 0;      // promillea viesteistä toimitetaan kahdesti
    int ajautuma_max = 0;  // kellon ajautuma enintään +-promillea
    Aika poikkeama_max = 0;  // kellon alkupoikkeama enintään +-ms
};
// @loppu asetukset

struct Tyhja {};  // pysyvä tila solmuille, joilla sitä ei ole

struct Tilasto {
    long lahetetty = 0, toimitettu = 0, kadonnut = 0, monistettu = 0,
         estetty = 0;
};

template <class V, class P = Tyhja>
class Simulaattori {
public:
    using Tehdas = std::function<std::unique_ptr<Solmu<V>>(int, P&)>;

    Simulaattori(int solmuja, std::uint64_t siemen, Verkkoasetukset a,
                 Tehdas tehdas)
        : asetukset_(a), tehdas_(std::move(tehdas)), verkko_(siemen),
          levyt_(static_cast<std::size_t>(solmuja)) {
        for (int i = 0; i < solmuja; ++i) {
            Tila t{.yhteys = Paikka(*this, i),
                   .satunnainen = Satunnainen(siemen, 1000 + i)};
            t.ajautuma = verkko_.valilta(-a.ajautuma_max, a.ajautuma_max);
            t.poikkeama = verkko_.valilta(-a.poikkeama_max,
                                          a.poikkeama_max);
            tilat_.push_back(std::move(t));
        }
        for (int i = 0; i < solmuja; ++i) kaynnista(i);
    }

    Simulaattori(const Simulaattori&) = delete;
    Simulaattori& operator=(const Simulaattori&) = delete;

    // @alku ajo
    // Käsittelee tapahtumat aikajärjestyksessä hetkeen `asti` saakka.
    // Saman hetken tapahtumat käsitellään lisäysjärjestyksessä.
    void aja(Aika asti) {
        while (!jono_.empty() && jono_.top().aika <= asti) {
            Tapahtuma t = jono_.top();
            jono_.pop();
            nyt_ = t.aika;
            kasittele(t);
            if (tarkistus_) tarkistus_();
        }
        nyt_ = asti;
    }
    // @loppu ajo

    // Testin toimenpide tiettynä hetkenä (vika, asiakaskutsu, ...).
    void kun(Aika aika, std::function<void()> toiminto) {
        lisaa(Tapahtuma{.aika = aika, .laji = Laji::Toiminto,
                        .toiminto = std::move(toiminto)});
    }

    // Kutsutaan jokaisen tapahtuman jälkeen: invariantit.
    void jokaisen_jalkeen(std::function<void()> f) {
        tarkistus_ = std::move(f);
    }

    // @alku viat
    void kaada(int i) {
        auto& t = tilat_[ind(i)];
        if (!t.solmu) return;
        t.solmu.reset();          // haihtuva tila katoaa
        ++t.aikakausi;            // vanhat ajastimet mitätöityvät
        kirjaa_sim(i, "kaatui");
    }

    void kaynnista(int i) {
        auto& t = tilat_[ind(i)];
        if (t.solmu) return;
        t.solmu = tehdas_(i, levyt_[ind(i)]);
        t.solmu->kaynnisty(t.yhteys);
    }

    // Jakaa verkon ryhmiin: viesti ryhmästä toiseen katoaa. Solmut,
    // joita ei mainita, jäävät yhteiseen ryhmään 0.
    void jaa(const std::vector<std::vector<int>>& ryhmat) {
        for (auto& t : tilat_) t.ryhma = 0;
        int nro = 1;
        for (const auto& r : ryhmat) {
            for (int i : r) tilat_[ind(i)].ryhma = nro;
            ++nro;
        }
    }
    void paranna() { jaa({}); }

    // Solmuparin kiinteä lisäviive (esim. eri konesalit).
    void lisaviive(std::function<Aika(int, int)> f) {
        lisaviive_ = std::move(f);
    }

    // Vaihtaa verkon ominaisuudet kesken ajon (esim. ruuhka).
    void verkko(Verkkoasetukset a) {
        a.ajautuma_max = asetukset_.ajautuma_max;
        a.poikkeama_max = asetukset_.poikkeama_max;
        asetukset_ = a;
    }
    // @loppu viat

    bool elossa(int i) const { return tilat_[ind(i)].solmu != nullptr; }
    bool yhteys(int a, int b) const {
        return tilat_[ind(a)].ryhma == tilat_[ind(b)].ryhma;
    }
    int solmuja() const { return static_cast<int>(tilat_.size()); }
    Aika nyt() const { return nyt_; }
    const Tilasto& tilasto() const { return tilasto_; }
    P& levy(int i) { return levyt_[ind(i)]; }
    void tulosta_loki(bool k) { tulosta_ = k; }

    // Solmun olio tarkistuksia varten; nullptr, jos solmu on kaatunut.
    template <class T>
    T* solmu(int i) {
        return dynamic_cast<T*>(tilat_[ind(i)].solmu.get());
    }

private:
    enum class Laji { Viesti, Ajastin, Toiminto };

    struct Tapahtuma {
        Aika aika = 0;
        std::uint64_t jarjestys = 0;
        Laji laji = Laji::Toiminto;
        int kohde = 0, lahettaja = 0, tunniste = 0;
        std::uint64_t aikakausi = 0;
        std::optional<V> viesti{};
        std::function<void()> toiminto{};
    };
    struct Myohempi {
        bool operator()(const Tapahtuma& a, const Tapahtuma& b) const {
            return a.aika != b.aika ? a.aika > b.aika
                                    : a.jarjestys > b.jarjestys;
        }
    };

    class Paikka final : public Yhteys<V> {
    public:
        Paikka(Simulaattori& s, int i) : s_(&s), i_(i) {}
        int oma() const override { return i_; }
        int solmuja() const override { return s_->solmuja(); }
        Aika kello() const override { return s_->kello(i_); }
        void laheta(int kohde, V v) override {
            s_->laheta(i_, kohde, std::move(v));
        }
        void ajasta(Aika viive, int tunniste) override {
            s_->ajasta(i_, viive, tunniste);
        }
        Satunnainen& satunnainen() override {
            return s_->tilat_[ind(i_)].satunnainen;
        }
        void kirjaa(const std::string& rivi) override {
            s_->kirjaa_sim(i_, rivi);
        }
    private:
        Simulaattori* s_;
        int i_;
    };

    struct Tila {
        Paikka yhteys;
        Satunnainen satunnainen;
        std::unique_ptr<Solmu<V>> solmu{};
        std::uint64_t aikakausi = 0;
        int ryhma = 0;
        std::int64_t ajautuma = 0, poikkeama = 0;
    };

    static std::size_t ind(int i) { return static_cast<std::size_t>(i); }

    Aika kello(int i) const {
        const auto& t = tilat_[ind(i)];
        return nyt_ + t.poikkeama + nyt_ * t.ajautuma / 1000;
    }

    // @alku laheta
    void laheta(int lahettaja, int kohde, V v) {
        ++tilasto_.lahetetty;
        if (verkko_.tapahtuu(asetukset_.katoaa)) {
            ++tilasto_.kadonnut;
            return;
        }
        Aika lisa = lisaviive_ ? lisaviive_(lahettaja, kohde) : 0;
        Aika viive = lisa + verkko_.valilta(asetukset_.viive_min,
                                            asetukset_.viive_max);
        if (verkko_.tapahtuu(asetukset_.monistuu)) {
            ++tilasto_.monistettu;
            Aika toinen = lisa + verkko_.valilta(asetukset_.viive_min,
                                                 asetukset_.viive_max);
            lisaa(Tapahtuma{.aika = nyt_ + toinen, .laji = Laji::Viesti,
                            .kohde = kohde, .lahettaja = lahettaja,
                            .viesti = v});
        }
        lisaa(Tapahtuma{.aika = nyt_ + viive, .laji = Laji::Viesti,
                        .kohde = kohde, .lahettaja = lahettaja,
                        .viesti = std::move(v)});
    }
    // @loppu laheta

    void ajasta(int i, Aika viive, int tunniste) {
        lisaa(Tapahtuma{.aika = nyt_ + viive, .laji = Laji::Ajastin,
                        .kohde = i, .tunniste = tunniste,
                        .aikakausi = tilat_[ind(i)].aikakausi});
    }

    void lisaa(Tapahtuma t) {
        t.jarjestys = seuraava_++;
        jono_.push(std::move(t));
    }

    void kasittele(const Tapahtuma& t) {
        if (t.laji == Laji::Toiminto) {
            t.toiminto();
            return;
        }
        auto& kohde = tilat_[ind(t.kohde)];
        if (t.laji == Laji::Ajastin) {
            if (kohde.solmu && t.aikakausi == kohde.aikakausi)
                kohde.solmu->ajastin(kohde.yhteys, t.tunniste);
            return;
        }
        if (!yhteys(t.lahettaja, t.kohde)) {
            ++tilasto_.estetty;   // verkko on jaettu saapumishetkellä
            return;
        }
        if (!kohde.solmu) {
            ++tilasto_.kadonnut;  // vastaanottaja on kaatunut
            return;
        }
        ++tilasto_.toimitettu;
        kohde.solmu->vastaanota(kohde.yhteys, t.lahettaja, *t.viesti);
    }

    void kirjaa_sim(int i, const std::string& rivi) {
        if (tulosta_)
            std::printf("%6lld s%d: %s\n", static_cast<long long>(nyt_),
                        i, rivi.c_str());
    }

    Verkkoasetukset asetukset_;
    Tehdas tehdas_;
    Satunnainen verkko_;
    std::vector<P> levyt_;
    std::vector<Tila> tilat_;
    std::priority_queue<Tapahtuma, std::vector<Tapahtuma>, Myohempi>
        jono_;
    std::uint64_t seuraava_ = 0;
    Aika nyt_ = 0;
    Tilasto tilasto_;
    bool tulosta_ = false;
    std::function<void()> tarkistus_;
    std::function<Aika(int, int)> lisaviive_;
};
