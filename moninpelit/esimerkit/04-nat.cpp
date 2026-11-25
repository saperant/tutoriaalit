// NAT-läpäisyn periaate: kotireititin päästää sisään vain liikennettä,
// joka vastaa sisäverkosta lähteneeseen. Kaksi pelaajaa NATin takana
// saa suoran yhteyden, kun kumpikin lähettää ensin toiselle (reiän
// avaaminen, hole punching). Osoitteet välittää yhteinen palvelin.
#include <compare>
#include <print>
#include <set>
#include <string_view>

struct Osoite {
    int kone, portti;
    auto operator<=>(const Osoite&) const = default;
};

// @alku nat
// Osoitteenmuunnos pelkistettynä: ulos lähtevä paketti luo säännön,
// ja sisään pääsee vain säännön mukaisesta osoitteesta tuleva paketti.
class Nat {
public:
    void ulos(Osoite kohde) { sallitut_.insert(kohde); }
    bool sisaan(Osoite lahde) const { return sallitut_.contains(lahde); }

private:
    std::set<Osoite> sallitut_;
};

struct Pelaaja {
    std::string_view nimi;
    Osoite julkinen;  // osoite, jona NAT näyttää pelaajan ulospäin
    Nat nat;
};

// Paketti lähettäjältä vastaanottajalle molempien NATien läpi.
bool laheta(Pelaaja& lahettaja, Pelaaja& vastaanottaja) {
    lahettaja.nat.ulos(vastaanottaja.julkinen);
    const bool perille = vastaanottaja.nat.sisaan(lahettaja.julkinen);
    std::println("{} -> {}: {}", lahettaja.nimi, vastaanottaja.nimi,
                 perille ? "perillä" : "pudotettu vastaanottajan NATissa");
    return perille;
}
// @loppu nat

int main() {
    Pelaaja a{"A", {1, 5000}, {}}, b{"B", {2, 6000}, {}};
    std::println("ilman valmistelua:");
    Pelaaja c{"C", {3, 7000}, {}};
    laheta(c, b);

    // @alku reika
    // Kumpikin on kysynyt yhteispalvelimelta toisen julkisen osoitteen.
    // Ensimmäinen paketti putoaa, mutta avaa lähettäjän oman NATin.
    std::println("reiän avaaminen:");
    laheta(a, b);
    laheta(b, a);
    laheta(a, b);
    // @loppu reika
}
