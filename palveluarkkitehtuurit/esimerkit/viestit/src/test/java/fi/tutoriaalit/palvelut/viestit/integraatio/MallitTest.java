package fi.tutoriaalit.palvelut.viestit.integraatio;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;
import org.junit.jupiter.api.Test;

class MallitTest {
    // @alku putki
    @Test
    void vanhaTilausKulkeeKanavienLapi() {
        var kanavat = new HashMap<String, List<Sanoma>>();
        var kuolleet = new ArrayList<String>();     // Dead Letter Channel
        var reititin = Mallit.reititin(Map.of("FI", "kotimaa"), "ulkomaa");
        List<String> sisaan = List.of(
                "TILAUS;T-1;FI;kahvinkeitin:1,suodatin:0,pussit:3",
                "TILAUS;T-2;SE;vedenkeitin:2",
                "TILAUS-V2;rikki");
        for (String rivi : sisaan) {
            Sanoma tilaus;
            try {
                tilaus = Mallit.kaanna(rivi);
            } catch (IllegalArgumentException e) {
                kuolleet.add(rivi);
                continue;
            }
            for (Sanoma osa : Mallit.pilko(tilaus)) {
                if (Mallit.eiNollarivia().test(osa)) {
                    kanavat.computeIfAbsent(reititin.apply(osa),
                            k -> new ArrayList<>()).add(osa);
                }
            }
        }
        assertThat(kanavat.get("kotimaa")).extracting(Sanoma::runko)
            .containsExactly("kahvinkeitin:1", "pussit:3");
        assertThat(kanavat.get("ulkomaa")).extracting(Sanoma::runko)
            .containsExactly("vedenkeitin:2");
        assertThat(kuolleet).containsExactly("TILAUS-V2;rikki");
    }
    // @loppu putki

    // @alku kokooja
    @Test
    void kokoojaOdottaaKaikkiOsat() {
        var osat = new ArrayList<>(Mallit.pilko(Mallit.kaanna(
                "TILAUS;T-3;FI;a:1,b:2,c:3")));
        Collections.shuffle(osat, new Random(7));
        var kokooja = new Mallit.Kokooja();
        assertThat(kokooja.vastaanota(osat.get(0))).isEmpty();
        assertThat(kokooja.vastaanota(osat.get(1))).isEmpty();
        var kooste = kokooja.vastaanota(osat.get(2)).orElseThrow();
        assertThat(kooste.runko()).isEqualTo("a:1,b:2,c:3");
        assertThat(kooste.otsake("korrelaatio")).isEqualTo("T-3");
    }
    // @loppu kokooja
}
