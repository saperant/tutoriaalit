// punamusta.hpp: vasemmalle kallistuva punamusta puu (Sedgewick 2008).
//
// Punainen linkki yhdistää solmun vanhempaansa samaksi 2-3-puun
// 3-solmuksi. Punaiset linkit osoittavat aina vasemmalle, joten jokaista
// 2-3-puuta vastaa täsmälleen yksi punamusta puu.
#pragma once

#include <algorithm>
#include <memory>
#include <optional>
#include <string>
#include <vector>

class PunamustaPuu {
public:
    bool sisaltaa(int x) const
    {
        const Solmu* h = juuri_.get();
        while (h != nullptr) {
            if (x == h->avain) {
                return true;
            }
            h = x < h->avain ? h->vasen.get() : h->oikea.get();
        }
        return false;
    }

    void lisaa(int x)
    {
        juuri_ = lisaa(std::move(juuri_), x);
        juuri_->punainen = false;
    }

    void poista(int x)
    {
        if (!sisaltaa(x)) {
            return;
        }
        if (!punainen(juuri_->vasen) && !punainen(juuri_->oikea)) {
            juuri_->punainen = true;
        }
        juuri_ = poista(std::move(juuri_), x);
        if (juuri_) {
            juuri_->punainen = false;
        }
    }

    int korkeus() const { return korkeus(juuri_.get()); }

    std::vector<int> alkiot() const
    {
        std::vector<int> tulos;
        sisajarjestys(juuri_.get(), tulos);
        return tulos;
    }

    // Tarkistaa invariantit. Palauttaa ensimmäisen rikkeen kuvauksen tai
    // tyhjän, jos puu on kunnossa.
    std::optional<std::string> tarkista() const
    {
        if (punainen(juuri_)) {
            return "juuri on punainen";
        }
        std::optional<std::string> rike;
        mustat(juuri_.get(), nullptr, nullptr, rike);
        return rike;
    }

private:
    struct Solmu {
        explicit Solmu(int a) : avain{a} {}
        int avain;
        bool punainen = true;   // uusi solmu liitetään punaisella
        std::unique_ptr<Solmu> vasen, oikea;
    };
    using Osoitin = std::unique_ptr<Solmu>;

    static bool punainen(const Osoitin& h) { return h && h->punainen; }

    // @alku kierrot
    // Kierto vasemmalle: oikea punainen lapsi x nousee h:n paikalle ja
    // perii sen värin; h laskeutuu x:n punaiseksi vasemmaksi lapseksi.
    // Sisäjärjestys säilyy: (a h (b x c)) muuttuu muotoon ((a h b) x c).
    static Osoitin kierra_vasen(Osoitin h)
    {
        Osoitin x = std::move(h->oikea);
        h->oikea = std::move(x->vasen);
#ifndef KIERTOVIRHE
        x->punainen = h->punainen;
#endif
        h->punainen = true;
        x->vasen = std::move(h);
        return x;
    }

    static Osoitin kierra_oikea(Osoitin h)
    {
        Osoitin x = std::move(h->vasen);
        h->vasen = std::move(x->oikea);
        x->punainen = h->punainen;
        h->punainen = true;
        x->oikea = std::move(h);
        return x;
    }

    // Värinvaihto halkaisee 2-3-4-puun 4-solmun: lapset mustiksi ja
    // keskimmäinen avain nousee punaisella linkillä vanhempaan.
    static void vaihda_varit(Solmu& h)
    {
        h.punainen = !h.punainen;
        h.vasen->punainen = !h.vasen->punainen;
        h.oikea->punainen = !h.oikea->punainen;
    }
    // @loppu kierrot

    // @alku lisays
    // Kolme korjausta paluumatkalla korjaavat jokaisen mahdollisen
    // rikkeen: oikealle nojaava punainen, kaksi punaista peräkkäin ja
    // kaksi punaista lasta.
    static Osoitin tasapainota(Osoitin h)
    {
        if (punainen(h->oikea) && !punainen(h->vasen)) {
            h = kierra_vasen(std::move(h));
        }
        if (punainen(h->vasen) && punainen(h->vasen->vasen)) {
            h = kierra_oikea(std::move(h));
        }
        if (punainen(h->vasen) && punainen(h->oikea)) {
            vaihda_varit(*h);
        }
        return h;
    }

    static Osoitin lisaa(Osoitin h, int x)
    {
        if (!h) {
            return std::make_unique<Solmu>(x);
        }
        if (x < h->avain) {
            h->vasen = lisaa(std::move(h->vasen), x);
        } else if (x > h->avain) {
            h->oikea = lisaa(std::move(h->oikea), x);
        }
        return tasapainota(std::move(h));
    }
    // @loppu lisays

    // @alku poisto
    // Poisto laskeutuu puussa niin, että nykyinen solmu ei ole koskaan
    // 2-solmu: tarvittaessa lainataan avain sisarukselta tai yhdistetään
    // sen kanssa. Poistettava avain on silloin aina 3- tai 4-solmussa,
    // ja lehdestä sen voi poistaa rikkomatta mustaa korkeutta.
    static Osoitin siirra_punainen_vasemmalle(Osoitin h)
    {
        vaihda_varit(*h);
        if (punainen(h->oikea->vasen)) {
            h->oikea = kierra_oikea(std::move(h->oikea));
            h = kierra_vasen(std::move(h));
            vaihda_varit(*h);
        }
        return h;
    }

    static Osoitin siirra_punainen_oikealle(Osoitin h)
    {
        vaihda_varit(*h);
        if (punainen(h->vasen->vasen)) {
            h = kierra_oikea(std::move(h));
            vaihda_varit(*h);
        }
        return h;
    }

    static Osoitin poista_pienin(Osoitin h)
    {
        if (!h->vasen) {
            return nullptr;
        }
        if (!punainen(h->vasen) && !punainen(h->vasen->vasen)) {
            h = siirra_punainen_vasemmalle(std::move(h));
        }
        h->vasen = poista_pienin(std::move(h->vasen));
        return tasapainota(std::move(h));
    }

    static Osoitin poista(Osoitin h, int x)
    {
        if (x < h->avain) {
            if (!punainen(h->vasen) && !punainen(h->vasen->vasen)) {
                h = siirra_punainen_vasemmalle(std::move(h));
            }
            h->vasen = poista(std::move(h->vasen), x);
        } else {
            if (punainen(h->vasen)) {
                h = kierra_oikea(std::move(h));
            }
            if (x == h->avain && !h->oikea) {
                return nullptr;
            }
            if (!punainen(h->oikea) && !punainen(h->oikea->vasen)) {
                h = siirra_punainen_oikealle(std::move(h));
            }
            if (x == h->avain) {
                const Solmu* seuraaja = h->oikea.get();
                while (seuraaja->vasen) {
                    seuraaja = seuraaja->vasen.get();
                }
                h->avain = seuraaja->avain;
                h->oikea = poista_pienin(std::move(h->oikea));
            } else {
                h->oikea = poista(std::move(h->oikea), x);
            }
        }
        return tasapainota(std::move(h));
    }
    // @loppu poisto

    static int korkeus(const Solmu* h)
    {
        return h ? 1 + std::max(korkeus(h->vasen.get()),
                                korkeus(h->oikea.get()))
                 : 0;
    }

    static void sisajarjestys(const Solmu* h, std::vector<int>& tulos)
    {
        if (h) {
            sisajarjestys(h->vasen.get(), tulos);
            tulos.push_back(h->avain);
            sisajarjestys(h->oikea.get(), tulos);
        }
    }

    // @alku invariantit
    // Palauttaa alipuun mustan korkeuden ja kirjaa ensimmäisen rikkeen.
    // ala ja yla ovat avainten aidot rajat (nullptr = ei rajaa).
    static int mustat(const Solmu* h, const int* ala, const int* yla,
                      std::optional<std::string>& rike)
    {
        if (!h || rike) {
            return 0;
        }
        auto kirjaa = [&](const char* kuvaus) {
            rike = std::string{kuvaus} + " (avain "
                + std::to_string(h->avain) + ")";
        };
        if ((ala && h->avain <= *ala) || (yla && h->avain >= *yla)) {
            kirjaa("hakupuun järjestys rikki");
        } else if (punainen(h->oikea)) {
            kirjaa("punainen oikea linkki");
        } else if (h->punainen && punainen(h->vasen)) {
            kirjaa("kaksi punaista peräkkäin");
        }
        int v = mustat(h->vasen.get(), ala, &h->avain, rike);
        int o = mustat(h->oikea.get(), &h->avain, yla, rike);
        if (v != o && !rike) {
            kirjaa("mustat korkeudet eroavat");
        }
        return v + (h->punainen ? 0 : 1);
    }
    // @loppu invariantit

    Osoitin juuri_;
};
