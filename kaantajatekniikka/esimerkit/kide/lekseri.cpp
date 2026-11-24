#include "lekseri.hpp"

#include <limits>
#include <unordered_map>

namespace kide {

namespace {

const std::unordered_map<std::string_view, Laji> kAvainsanat = {
    {"fn", Laji::Fn},         {"var", Laji::Var},
    {"if", Laji::If},         {"else", Laji::Else},
    {"while", Laji::While},   {"return", Laji::Return},
    {"print", Laji::Print},   {"true", Laji::True},
    {"false", Laji::False},   {"int", Laji::Int},
    {"bool", Laji::Bool},
};

bool kirjain(char c) {
    return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || c == '_';
}
bool numero(char c) { return c >= '0' && c <= '9'; }

class Selain {
public:
    Selain(std::string_view lahde, Diagnostiikka& diag)
        : lahde_(lahde), diag_(diag) {}
    std::vector<Tokeni> selaa();

private:
    char katso(std::size_t n = 0) const {
        return kohta_ + n < lahde_.size() ? lahde_[kohta_ + n] : '\0';
    }
    char seuraava() {
        char c = lahde_[kohta_++];
        if (c == '\n') {
            ++rivi_;
            sarake_ = 1;
        } else {
            ++sarake_;
        }
        return c;
    }
    bool vastaa(char odotettu) {
        if (katso() != odotettu) return false;
        seuraava();
        return true;
    }
    void ohita_tyhja();
    std::int64_t luku(Sijainti alku);
    bool operaattori(char c, Sijainti alku, Laji& laji);

    std::string_view lahde_;
    Diagnostiikka& diag_;
    std::size_t kohta_ = 0;
    int rivi_ = 1;
    int sarake_ = 1;
};

// @alku tyhja
void Selain::ohita_tyhja() {
    for (;;) {
        char c = katso();
        if (c == ' ' || c == '\t' || c == '\r' || c == '\n') {
            seuraava();
        } else if (c == '/' && katso(1) == '/') {
            while (kohta_ < lahde_.size() && katso() != '\n') seuraava();
        } else {
            return;
        }
    }
}
// @loppu tyhja

// @alku luku
// Desimaaliluku. Ylivuoto tarkistetaan ennen kertolaskua, koska
// etumerkillisen luvun ylivuoto olisi C++:ssa määrittelemätöntä.
// Virheellinen luku raportoidaan, mutta tokeni syntyy silti (arvo 0),
// jotta jäsennin ei tuota virheestä uusia seurannaisvirheitä.
std::int64_t Selain::luku(Sijainti alku) {
    constexpr auto kSuurin = std::numeric_limits<std::int64_t>::max();
    bool ylivuoto = false;
    std::int64_t arvo = lahde_[kohta_ - 1] - '0';
    while (numero(katso())) {
        int d = seuraava() - '0';
        if (arvo > (kSuurin - d) / 10) ylivuoto = true;
        if (!ylivuoto) arvo = arvo * 10 + d;
    }
    if (kirjain(katso())) {
        while (kirjain(katso()) || numero(katso())) seuraava();
        diag_.virhe(alku, "virheellinen luku");
        return 0;
    }
    if (ylivuoto) {
        diag_.virhe(alku, "kokonaisluku ei mahdu 64 bittiin");
        return 0;
    }
    return arvo;
}
// @loppu luku

bool Selain::operaattori(char c, Sijainti alku, Laji& laji) {
    switch (c) {
    case '+': laji = Laji::Plus; return true;
    case '*': laji = Laji::Tahti; return true;
    case '/': laji = Laji::Kautta; return true;
    case '%': laji = Laji::Prosentti; return true;
    case ':': laji = Laji::Kaksoispiste; return true;
    case ',': laji = Laji::Pilkku; return true;
    case ';': laji = Laji::Puolipiste; return true;
    case '(': laji = Laji::VasenSulku; return true;
    case ')': laji = Laji::OikeaSulku; return true;
    case '{': laji = Laji::VasenAalto; return true;
    case '}': laji = Laji::OikeaAalto; return true;
// @alku pisin
    // Pisin osuma: "->" ennen "-", "==" ennen "=" ja niin edelleen.
    case '-': laji = vastaa('>') ? Laji::Nuoli : Laji::Miinus; return true;
    case '=': laji = vastaa('=') ? Laji::Yhtasuuri : Laji::Sijoitus;
              return true;
    case '!': laji = vastaa('=') ? Laji::Erisuuri : Laji::Ei; return true;
    case '<': laji = vastaa('=') ? Laji::PienempiYhta : Laji::Pienempi;
              return true;
    case '>': laji = vastaa('=') ? Laji::SuurempiYhta : Laji::Suurempi;
              return true;
    case '&':
    case '|':
        // Yksinäinen & tai | raportoidaan, ja tulkitaan && tai ||.
        if (!vastaa(c)) {
            diag_.virhe(alku, std::string("odotettiin '") + c + c + "'");
        }
        laji = c == '&' ? Laji::Ja : Laji::Tai;
        return true;
// @loppu pisin
    default:
        break;
    }
    const char* heksa = "0123456789abcdef";
    auto u = static_cast<unsigned char>(c);
    std::string merkki = u >= 0x20 && u < 0x7f
        ? std::string("'") + c + "'"
        : std::string("0x") + heksa[u >> 4] + heksa[u & 15];
    diag_.virhe(alku, "tuntematon merkki " + merkki);
    return false;
}

// @alku selaa
std::vector<Tokeni> Selain::selaa() {
    std::vector<Tokeni> tokenit;
    for (;;) {
        ohita_tyhja();
        Sijainti alku{rivi_, sarake_};
        std::size_t alkukohta = kohta_;
        if (kohta_ >= lahde_.size()) {
            tokenit.push_back({Laji::Loppu, "", alku});
            return tokenit;
        }
        char c = seuraava();
        Laji laji = Laji::Loppu;
        std::int64_t arvo = 0;
        if (kirjain(c)) {
            while (kirjain(katso()) || numero(katso())) seuraava();
            auto sana = lahde_.substr(alkukohta, kohta_ - alkukohta);
            auto avain = kAvainsanat.find(sana);
            laji = avain != kAvainsanat.end() ? avain->second
                                              : Laji::Tunniste;
        } else if (numero(c)) {
            arvo = luku(alku);
            laji = Laji::Luku;
        } else if (!operaattori(c, alku, laji)) {
            continue;  // virhe raportoitu, jatketaan seuraavasta
        }
        tokenit.push_back(
            {laji, std::string(lahde_.substr(alkukohta, kohta_ - alkukohta)),
             alku, arvo});
    }
}
// @loppu selaa

}  // namespace

std::string kuvaus(Laji laji) {
    switch (laji) {
    case Laji::Luku: return "kokonaisluku";
    case Laji::Tunniste: return "tunniste";
    case Laji::Loppu: return "tiedoston loppu";
    case Laji::Fn: return "'fn'";
    case Laji::Var: return "'var'";
    case Laji::If: return "'if'";
    case Laji::Else: return "'else'";
    case Laji::While: return "'while'";
    case Laji::Return: return "'return'";
    case Laji::Print: return "'print'";
    case Laji::True: return "'true'";
    case Laji::False: return "'false'";
    case Laji::Int: return "'int'";
    case Laji::Bool: return "'bool'";
    case Laji::Plus: return "'+'";
    case Laji::Miinus: return "'-'";
    case Laji::Tahti: return "'*'";
    case Laji::Kautta: return "'/'";
    case Laji::Prosentti: return "'%'";
    case Laji::Yhtasuuri: return "'=='";
    case Laji::Erisuuri: return "'!='";
    case Laji::Pienempi: return "'<'";
    case Laji::PienempiYhta: return "'<='";
    case Laji::Suurempi: return "'>'";
    case Laji::SuurempiYhta: return "'>='";
    case Laji::Ja: return "'&&'";
    case Laji::Tai: return "'||'";
    case Laji::Ei: return "'!'";
    case Laji::Sijoitus: return "'='";
    case Laji::Nuoli: return "'->'";
    case Laji::Kaksoispiste: return "':'";
    case Laji::Pilkku: return "','";
    case Laji::Puolipiste: return "';'";
    case Laji::VasenSulku: return "'('";
    case Laji::OikeaSulku: return "')'";
    case Laji::VasenAalto: return "'{'";
    case Laji::OikeaAalto: return "'}'";
    }
    return "?";
}

std::vector<Tokeni> selaa(std::string_view lahde, Diagnostiikka& diag) {
    return Selain(lahde, diag).selaa();
}

}  // namespace kide
