// Raft-konsensus (Ongaro ja Ousterhout 2014) simulaattorin solmuna:
// johtajavaali, lokin replikointi, sitoutuminen ja tilakone. Lisäksi
// tarkkailija, joka tarkistaa Raftin turvallisuusominaisuudet.
//
// Opetusta varten kaksi tunnettua virhettä voi kytkeä päälle makroilla
// ennen tämän otsakkeen sisällyttämistä:
//   RAFT_BUGI_AANESTYS   ääni annetaan tarkistamatta ehdokkaan lokia
//   RAFT_BUGI_SITOUTUS   edellisen termin merkintä sitoutetaan pelkän
//                        enemmistön perusteella
// Makro RAFT_ILMAN_TYHJAA jättää pois tyhjän merkinnän, jonka johtaja
// lisää termin alussa.
#pragma once
#include <algorithm>
#include <map>
#include <memory>
#include <set>
#include <string>
#include <vector>

#include "simulaattori.hpp"

// @alku tyypit
struct Merkinta {
    int termi;
    int komento;      // 0 = johtajan termin alussa lisäämä tyhjä merkintä
    bool operator==(const Merkinta&) const = default;
};

// Raftin pysyvä tila: säilyy kaatumisen yli.
struct RaftLevy {
    int termi = 0;
    int aanestetty = -1;
    std::vector<Merkinta> loki;     // indeksit alkavat ykkösestä
};

struct RaftViesti {
    enum class Laji { PyydaAania, Aani, Lisaa, LisaaVastaus, Komento,
                      KomentoVastaus } laji;
    int termi = 0;
    int indeksi = 0, indeksin_termi = 0;   // viimeinen tai edellinen
    int sitoutettu = 0;
    std::vector<Merkinta> merkinnat{};
    bool ok = false;
    int vastaava = 0;                      // seuraajan viimeinen indeksi
    int komento = 0, johtaja = -1;
};
// @loppu tyypit

// @alku tarkkailija
// Kirjaa jokaisen termin johtajan ja jokaisen sovelletun merkinnän ja
// ilmoittaa ensimmäisestä turvallisuusrikkeestä.
class Tarkkailija {
public:
    void johtaja(Aika t, int termi, int solmu) {
        auto [it, uusi] = johtajat_.insert({termi, solmu});
        if (!uusi && it->second != solmu)
            virhe(t, "kaksi johtajaa termilla " + std::to_string(termi));
    }
    void sovellettu(Aika t, int solmu, int indeksi, Merkinta m) {
        auto [it, uusi] = sovelletut_.insert({indeksi, m});
        if (!uusi && !(it->second == m))
            virhe(t, "solmu " + std::to_string(solmu) + " sovelsi eri "
                     "merkinnan indeksiin " + std::to_string(indeksi));
        ++sovelluksia;
    }
    // Johtaja sitoutti merkinnän termillään.
    void sitoutettu(int indeksi, Merkinta m, int termi) {
        sitoutetut.insert({indeksi, {m, termi}});
    }
    void virhe(Aika t, const std::string& s) {
        if (ensimmainen.empty())
            ensimmainen = "t=" + std::to_string(t) + ": " + s;
    }
    struct Sitoutus {
        Merkinta merkinta;
        int termi;
    };
    std::map<int, Sitoutus> sitoutetut;
    std::string ensimmainen;       // tyhjä, jos rikettä ei ole havaittu
    long sovelluksia = 0;
    long vanhan_termin_sitoutuksia = 0;   // vain RAFT_BUGI_SITOUTUS
    int termeja() const { return static_cast<int>(johtajat_.size()); }
private:
    std::map<int, int> johtajat_;
    std::map<int, Merkinta> sovelletut_;
};
// @loppu tarkkailija

class RaftSolmu final : public Solmu<RaftViesti> {
public:
    static constexpr Aika SYKE = 50;
    enum class Rooli { Seuraaja, Ehdokas, Johtaja };

    // Vaaliaikaraja arvotaan väliltä [vaali_min, vaali_max].
    RaftSolmu(int palvelimia, RaftLevy& levy, Tarkkailija& t,
              Aika vaali_min = 150, Aika vaali_max = 300)
        : n_(palvelimia), levy_(levy), tark_(t), vaali_min_(vaali_min),
          vaali_max_(vaali_max) {}

    Rooli rooli() const { return rooli_; }
    int termi() const { return levy_.termi; }
    int sitoutettu() const { return sitoutettu_; }
    const std::vector<Merkinta>& loki() const { return levy_.loki; }

    void kaynnisty(Yhteys<RaftViesti>& y) override { vaaliajastin(y); }

    void ajastin(Yhteys<RaftViesti>& y, int tunniste) override {
        if (tunniste < 0) {                     // johtajan syke
            if (rooli_ == Rooli::Johtaja && tunniste == -sykenro_) {
                for (int s = 0; s < n_; ++s)
                    if (s != y.oma()) lisaa(y, s);
                y.ajasta(SYKE, -sykenro_);
            }
        } else if (tunniste == vaalinro_ && rooli_ != Rooli::Johtaja) {
            aloita_vaali(y);
        }
    }

    void vastaanota(Yhteys<RaftViesti>& y, int l,
                    const RaftViesti& v) override {
        using L = RaftViesti::Laji;
        if (v.laji == L::Komento) return komento(y, l, v);
        if (v.laji == L::KomentoVastaus) return;
        if (v.termi > levy_.termi) {           // uudempi termi: seuraajaksi
            levy_.termi = v.termi;
            levy_.aanestetty = -1;
            rooli_ = Rooli::Seuraaja;
        }
        switch (v.laji) {
        case L::PyydaAania: return aanestys(y, l, v);
        case L::Aani: return aani(y, l, v);
        case L::Lisaa: return lisays(y, l, v);
        case L::LisaaVastaus: return lisays_vastaus(y, l, v);
        default: return;
        }
    }

private:
    int viimeinen() const { return static_cast<int>(levy_.loki.size()); }
    int termi_kohdassa(int i) const {
        return i == 0 ? 0 : levy_.loki[static_cast<size_t>(i - 1)].termi;
    }

    void vaaliajastin(Yhteys<RaftViesti>& y) {
        y.ajasta(y.satunnainen().valilta(vaali_min_, vaali_max_),
                 ++vaalinro_);
    }

    // @alku vaali
    void aloita_vaali(Yhteys<RaftViesti>& y) {
        ++levy_.termi;
        levy_.aanestetty = y.oma();
        rooli_ = Rooli::Ehdokas;
        aanet_ = {y.oma()};
        y.kirjaa("ehdokas termilla " + std::to_string(levy_.termi));
        for (int s = 0; s < n_; ++s)
            if (s != y.oma())
                y.laheta(s, {.laji = RaftViesti::Laji::PyydaAania,
                             .termi = levy_.termi, .indeksi = viimeinen(),
                             .indeksin_termi = termi_kohdassa(viimeinen())});
        vaaliajastin(y);
    }

    void aanestys(Yhteys<RaftViesti>& y, int ehdokas, const RaftViesti& v) {
        // Ehdokkaan loki on vähintään yhtä tuore kuin oma: viimeisen
        // merkinnän termi on suurempi, tai sama ja loki yhtä pitkä.
        bool tuore = v.indeksin_termi > termi_kohdassa(viimeinen()) ||
                     (v.indeksin_termi == termi_kohdassa(viimeinen()) &&
                      v.indeksi >= viimeinen());
#ifdef RAFT_BUGI_AANESTYS
        tuore = true;
#endif
        bool myonna = v.termi == levy_.termi && tuore &&
                      (levy_.aanestetty == -1 ||
                       levy_.aanestetty == ehdokas);
        if (myonna) {
            levy_.aanestetty = ehdokas;
            vaaliajastin(y);
        }
        y.laheta(ehdokas, {.laji = RaftViesti::Laji::Aani,
                           .termi = levy_.termi, .ok = myonna});
    }

    void aani(Yhteys<RaftViesti>& y, int l, const RaftViesti& v) {
        if (rooli_ != Rooli::Ehdokas || v.termi != levy_.termi || !v.ok)
            return;
        aanet_.insert(l);
        if (static_cast<int>(aanet_.size()) * 2 <= n_) return;
        rooli_ = Rooli::Johtaja;
        tark_.johtaja(y.kello(), levy_.termi, y.oma());
        y.kirjaa("johtaja termilla " + std::to_string(levy_.termi));
        seuraava_.assign(static_cast<size_t>(n_), viimeinen() + 1);
        vastaava_.assign(static_cast<size_t>(n_), 0);
#ifndef RAFT_ILMAN_TYHJAA
        levy_.loki.push_back({levy_.termi, 0});     // tyhjä merkintä
#endif
        vastaava_[static_cast<size_t>(y.oma())] = viimeinen();
        ++sykenro_;
        ajastin(y, -sykenro_);
    }
    // @loppu vaali

    // @alku replikointi
    void lisaa(Yhteys<RaftViesti>& y, int s) {
        int ed = seuraava_[static_cast<size_t>(s)] - 1;
        RaftViesti v{.laji = RaftViesti::Laji::Lisaa, .termi = levy_.termi,
                     .indeksi = ed, .indeksin_termi = termi_kohdassa(ed),
                     .sitoutettu = sitoutettu_};
        v.merkinnat.assign(levy_.loki.begin() + ed, levy_.loki.end());
        y.laheta(s, std::move(v));
    }

    void lisays(Yhteys<RaftViesti>& y, int johtaja, const RaftViesti& v) {
        RaftViesti vastaus{.laji = RaftViesti::Laji::LisaaVastaus,
                           .termi = levy_.termi};
        if (v.termi < levy_.termi) return y.laheta(johtaja, vastaus);
        rooli_ = Rooli::Seuraaja;
        johtaja_ = johtaja;
        vaaliajastin(y);
        if (v.indeksi > viimeinen() ||
            termi_kohdassa(v.indeksi) != v.indeksin_termi) {
            vastaus.vastaava = std::min(v.indeksi - 1, viimeinen());
            return y.laheta(johtaja, vastaus);       // aukko tai ristiriita
        }
        int i = v.indeksi;
        for (const Merkinta& m : v.merkinnat) {
            ++i;
            if (i <= viimeinen() && termi_kohdassa(i) != m.termi)
                levy_.loki.resize(static_cast<size_t>(i - 1));  // katkaise
            if (i > viimeinen()) levy_.loki.push_back(m);
        }
        if (v.sitoutettu > sitoutettu_)
            sitoutettu_ = std::min(v.sitoutettu, i);
        sovella(y);
        vastaus.ok = true;
        vastaus.vastaava = i;
        y.laheta(johtaja, vastaus);
    }

    void lisays_vastaus(Yhteys<RaftViesti>& y, int s, const RaftViesti& v) {
        if (rooli_ != Rooli::Johtaja || v.termi != levy_.termi) return;
        auto i = static_cast<size_t>(s);
        if (!v.ok) {
            seuraava_[i] = std::max(1, std::min(seuraava_[i] - 1,
                                                v.vastaava + 1));
            return lisaa(y, s);
        }
        vastaava_[i] = std::max(vastaava_[i], v.vastaava);
        seuraava_[i] = vastaava_[i] + 1;
        // Suurin indeksi, joka on enemmistöllä ja tämän termin merkintä.
        for (int k = viimeinen(); k > sitoutettu_; --k) {
            int lkm = 0;
            for (int x : vastaava_) lkm += x >= k;
            bool oma_termi = termi_kohdassa(k) == levy_.termi;
            bool hyvaksy = oma_termi;
#ifdef RAFT_BUGI_SITOUTUS
            hyvaksy = true;
#endif
            if (lkm * 2 > n_ && hyvaksy) {
                if (!oma_termi) ++tark_.vanhan_termin_sitoutuksia;
                for (int j = sitoutettu_ + 1; j <= k; ++j)
                    tark_.sitoutettu(
                        j, levy_.loki[static_cast<size_t>(j - 1)],
                        levy_.termi);
                sitoutettu_ = k;
                break;
            }
        }
        sovella(y);
    }
    // @loppu replikointi

    // @alku tilakone
    void sovella(Yhteys<RaftViesti>& y) {
        while (sovellettu_ < sitoutettu_) {
            ++sovellettu_;
            Merkinta m = levy_.loki[static_cast<size_t>(sovellettu_ - 1)];
            tark_.sovellettu(y.kello(), y.oma(), sovellettu_, m);
            auto it = odottavat_.find(sovellettu_);
            if (it != odottavat_.end()) {
                if (it->second.komento == m.komento)
                    y.laheta(it->second.asiakas,
                             {.laji = RaftViesti::Laji::KomentoVastaus,
                              .ok = true, .komento = m.komento});
                odottavat_.erase(it);
            }
        }
    }

    void komento(Yhteys<RaftViesti>& y, int asiakas, const RaftViesti& v) {
        if (rooli_ != Rooli::Johtaja)
            return y.laheta(asiakas,
                            {.laji = RaftViesti::Laji::KomentoVastaus,
                             .komento = v.komento, .johtaja = johtaja_});
        levy_.loki.push_back({levy_.termi, v.komento});
        vastaava_[static_cast<size_t>(y.oma())] = viimeinen();
        odottavat_[viimeinen()] = {asiakas, v.komento};
        for (int s = 0; s < n_; ++s)
            if (s != y.oma()) lisaa(y, s);
    }
    // @loppu tilakone

    struct Odottava {
        int asiakas, komento;
    };

    int n_;
    RaftLevy& levy_;
    Tarkkailija& tark_;
    Aika vaali_min_, vaali_max_;
    Rooli rooli_ = Rooli::Seuraaja;   // haihtuva tila alkaa tästä
    int johtaja_ = -1;
    int sitoutettu_ = 0, sovellettu_ = 0, vaalinro_ = 0, sykenro_ = 0;
    std::set<int> aanet_;
    std::vector<int> seuraava_, vastaava_;
    std::map<int, Odottava> odottavat_;
};

// @alku asiakas
// Lähettää komentoja yksi kerrallaan. Jos vastaaja ei ole johtaja, se
// kertoo tuntemansa johtajan; aikakatkaisun jälkeen kokeillaan
// satunnaista palvelinta.
class RaftAsiakas final : public Solmu<RaftViesti> {
public:
    explicit RaftAsiakas(int palvelimia) : n_(palvelimia) {}
    void kaynnisty(Yhteys<RaftViesti>& y) override { y.ajasta(50, 0); }

    void ajastin(Yhteys<RaftViesti>& y, int t) override {
        if (t == 0) {                       // uusi komento
            komento_ = y.oma() * 100000 + ++nro_;
        } else if (t != ajastin_) {
            return;                         // vanhentunut aikakatkaisu
        } else {
            kohde_ = static_cast<int>(y.satunnainen().valilta(0, n_ - 1));
        }
        laheta(y);
    }

    void vastaanota(Yhteys<RaftViesti>& y, int,
                    const RaftViesti& v) override {
        if (v.komento != komento_) return;
        if (v.ok) {
            ++valmiit;
            komento_ = -1;
            ++ajastin_;                     // aikakatkaisu ei enää koske
            y.ajasta(20, 0);
        } else if (v.johtaja >= 0 && v.johtaja != kohde_) {
            kohde_ = v.johtaja;
            laheta(y);
        }
    }
    int valmiit = 0;
private:
    void laheta(Yhteys<RaftViesti>& y) {
        y.laheta(kohde_, {.laji = RaftViesti::Laji::Komento,
                          .komento = komento_});
        y.ajasta(200, ++ajastin_);
    }
    int n_, kohde_ = 0, nro_ = 0, ajastin_ = 0, komento_ = -1;
};
// @loppu asiakas

// @alku lokien-tarkistus
// Lokien yhtäpitävyys: jos kahdella lokilla on samassa indeksissä
// saman termin merkintä, lokit ovat samat siihen asti. Johtajan
// täydellisyys: johtajan lokissa on jokainen sitoutettu merkintä.
template <class S>
void tarkista_lokit(S& sim, int palvelimia, Tarkkailija& t) {
    std::vector<RaftSolmu*> s;
    for (int i = 0; i < palvelimia; ++i)
        if (auto* p = sim.template solmu<RaftSolmu>(i)) s.push_back(p);
    for (auto* a : s) {
        for (auto* b : s) {
            size_t k = std::min(a->loki().size(), b->loki().size());
            while (k > 0 && a->loki()[k - 1].termi != b->loki()[k - 1].termi)
                --k;                       // viimeinen yhteinen termi
            if (!std::equal(a->loki().begin(), a->loki().begin() +
                            static_cast<long>(k), b->loki().begin()))
                t.virhe(sim.nyt(), "lokit eivat ole yhtapitavia");
        }
        if (a->rooli() != RaftSolmu::Rooli::Johtaja) continue;
        for (auto& [k, sit] : t.sitoutetut)
            if (sit.termi < a->termi() &&
                (static_cast<size_t>(k) > a->loki().size() ||
                 !(a->loki()[static_cast<size_t>(k - 1)] == sit.merkinta)))
                t.virhe(sim.nyt(), "termin " + std::to_string(a->termi()) +
                        " johtajalta puuttuu sitoutettu merkinta " +
                        std::to_string(k));
    }
}
// @loppu lokien-tarkistus
