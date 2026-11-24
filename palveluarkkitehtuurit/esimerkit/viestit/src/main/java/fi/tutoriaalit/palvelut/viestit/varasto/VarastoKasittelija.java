package fi.tutoriaalit.palvelut.viestit.varasto;

import fi.tutoriaalit.palvelut.viestit.yhteinen.Lahettaja;
import fi.tutoriaalit.palvelut.viestit.yhteinen.Saapuneet;
import fi.tutoriaalit.palvelut.viestit.yhteinen.Saapuneet.Vastaus;
import fi.tutoriaalit.palvelut.viestit.yhteinen.Viesti;
import jakarta.jms.JMSException;
import jakarta.jms.Message;
import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.jms.annotation.JmsListener;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

/** Varastopalvelu: käsittelee komennot VARAA ja VAPAUTA. */
@Component
class VarastoKasittelija {
    private final JdbcClient jdbc;
    private final Saapuneet saapuneet;
    private final Lahettaja lahettaja;

    VarastoKasittelija(JdbcClient jdbc, Lahettaja lahettaja) {
        this.jdbc = jdbc;
        this.saapuneet = new Saapuneet(jdbc, "varasto");
        this.lahettaja = lahettaja;
    }

    // @alku kasittele
    @JmsListener(destination = "varasto.komennot",
                 containerFactory = "jonot")
    @Transactional
    public void kasittele(Message jms) throws JMSException {
        Viesti v = Viesti.lue(jms);
        Vastaus vastaus = saapuneet.kasittele(v.id(), () ->
            switch (v.tyyppi()) {
                case "VARAA" -> varaa(v);
                case "VAPAUTA" -> vapauta(v);
                default -> throw new IllegalArgumentException(v.tyyppi());
            });
        // Vastaus lähtee samassa JMS-transaktiossa, jossa komento
        // kuitataan. Jos jokin pettää, komento toimitetaan uudelleen,
        // ja Saapuneet palauttaa saman vastauksen.
        lahettaja.laheta("myynti.vastaukset", "vastaus-" + v.id(),
                vastaus.tyyppi(), v.korrelaatio(), vastaus.runko());
    }

    private Vastaus varaa(Viesti v) {
        String tuote = v.runko().get("tuote").asString();
        int maara = v.runko().get("maara").asInt();
        int muutettu = jdbc.sql("""
                UPDATE varasto.saldo SET saldo = saldo - :maara
                WHERE tuote = :tuote AND saldo >= :maara""")
            .param("maara", maara).param("tuote", tuote).update();
        if (muutettu == 0) {
            return new Vastaus("VARAUS_EPAONNISTUI", "{}");
        }
        jdbc.sql("INSERT INTO varasto.varaus VALUES (?, ?, ?)")
            .params(v.korrelaatio(), tuote, maara).update();
        return new Vastaus("VARATTU", "{}");
    }
    // @loppu kasittele

    private Vastaus vapauta(Viesti v) {
        jdbc.sql("""
                UPDATE varasto.saldo SET saldo = saldo + (
                  SELECT maara FROM varasto.varaus WHERE tilaus_id = :id)
                WHERE tuote = (
                  SELECT tuote FROM varasto.varaus WHERE tilaus_id = :id)""")
            .param("id", v.korrelaatio()).update();
        jdbc.sql("DELETE FROM varasto.varaus WHERE tilaus_id = ?")
            .param(v.korrelaatio()).update();
        return new Vastaus("VAPAUTETTU", "{}");
    }
}
