package fi.tutoriaalit.palvelut.etakutsut.rpc;

/** Esimerkkirajapinta, jonka kutsulla on sivuvaikutus. */
public interface Tilauspalvelu {
    void tilaa(String tuote);
}
