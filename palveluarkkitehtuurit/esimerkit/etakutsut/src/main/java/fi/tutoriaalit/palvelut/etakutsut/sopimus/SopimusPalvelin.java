package fi.tutoriaalit.palvelut.etakutsut.sopimus;

import fi.tutoriaalit.palvelut.etakutsut.Palvelin;

/** Kuluttajan testeille: vastaa sopimuksen vastauksilla. */
public final class SopimusPalvelin {
    private SopimusPalvelin() {
    }

    public static Palvelin kaynnista(Sopimus sopimus) {
        return Palvelin.kaynnista(vaihto -> {
            var polku = vaihto.getRequestURI().getPath();
            var metodi = vaihto.getRequestMethod();
            for (var v : sopimus.vuorovaikutukset()) {
                if (v.pyynto().metodi().equals(metodi)
                        && v.pyynto().polku().equals(polku)) {
                    Palvelin.vastaa(vaihto, v.vastaus().tila(),
                            v.vastaus().runko().toString());
                    return;
                }
            }
            Palvelin.vastaa(vaihto, 500, "\"ei sopimuksessa\"");
        });
    }
}
