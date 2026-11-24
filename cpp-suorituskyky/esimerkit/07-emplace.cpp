// push_back, emplace_back ja try_emplace: montako oliota syntyy?
#include <map>
#include <string>
#include <utility>
#include <vector>

#include "seuranta.hpp"

int main()
{
    // @alku vektori
    std::vector<Seurattava> v;
    v.reserve(10);
    Seurattava::raportoi("(alku)");
    v.push_back(Seurattava{"a"});
    Seurattava::raportoi("push_back(Seurattava{...})");
    v.emplace_back("b");
    Seurattava::raportoi("emplace_back(\"b\")");
    Seurattava olemassa{"c"};
    Seurattava::raportoi("(olemassa oleva)");
    v.push_back(olemassa);
    Seurattava::raportoi("push_back(olemassa)");
    v.emplace_back(olemassa);
    Seurattava::raportoi("emplace_back(olemassa)");
    v.push_back(std::move(olemassa));
    Seurattava::raportoi("push_back(std::move(...))");
    // @loppu vektori

    // @alku kartta
    std::map<std::string, Seurattava> kartta;
    kartta.try_emplace("avain", "eka");
    Seurattava::raportoi("try_emplace, uusi avain");
    kartta.try_emplace("avain", "toka");
    Seurattava::raportoi("try_emplace, avain on jo");
    kartta.insert({"avain", Seurattava{"kolmas"}});
    Seurattava::raportoi("insert, avain on jo");
    // @loppu kartta
    std::printf("vektorissa %zu, kartassa %s\n", v.size(),
                kartta.at("avain").arvo.c_str());
}
