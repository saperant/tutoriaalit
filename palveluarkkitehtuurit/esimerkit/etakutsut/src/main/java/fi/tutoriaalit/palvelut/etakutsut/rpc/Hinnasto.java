package fi.tutoriaalit.palvelut.etakutsut.rpc;

import java.util.List;

/** Esimerkkirajapinta, joka voidaan toteuttaa paikallisesti tai etänä. */
public interface Hinnasto {
    int hinta(String tuote);

    List<String> tuotteet();
}
