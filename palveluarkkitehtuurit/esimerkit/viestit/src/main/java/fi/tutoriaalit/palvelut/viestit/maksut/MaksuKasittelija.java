package fi.tutoriaalit.palvelut.viestit.maksut;

import fi.tutoriaalit.palvelut.viestit.yhteinen.Lahettaja;
import fi.tutoriaalit.palvelut.viestit.yhteinen.Saapuneet;
import fi.tutoriaalit.palvelut.viestit.yhteinen.Saapuneet.Vastaus;
import fi.tutoriaalit.palvelut.viestit.yhteinen.Viesti;
import jakarta.jms.JMSException;
import jakarta.jms.Message;
import java.math.BigDecimal;
import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.jms.annotation.JmsListener;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

/** Maksupalvelu: veloittaa, jos summa mahtuu asiakkaan luottorajaan. */
@Component
class MaksuKasittelija {
    static final BigDecimal LUOTTORAJA = new BigDecimal("500.00");
    private final JdbcClient jdbc;
    private final Saapuneet saapuneet;
    private final Lahettaja lahettaja;

    MaksuKasittelija(JdbcClient jdbc, Lahettaja lahettaja) {
        this.jdbc = jdbc;
        this.saapuneet = new Saapuneet(jdbc, "maksut");
        this.lahettaja = lahettaja;
    }

    @JmsListener(destination = "maksut.komennot",
                 containerFactory = "jonot")
    @Transactional
    public void kasittele(Message jms) throws JMSException {
        Viesti v = Viesti.lue(jms);
        Vastaus vastaus = saapuneet.kasittele(v.id(), () -> veloita(v));
        lahettaja.laheta("myynti.vastaukset", "vastaus-" + v.id(),
                vastaus.tyyppi(), v.korrelaatio(), vastaus.runko());
    }

    private Vastaus veloita(Viesti v) {
        var summa = v.runko().get("summa").decimalValue();
        if (summa.compareTo(LUOTTORAJA) > 0) {
            return new Vastaus("MAKSU_HYLATTY", "{}");
        }
        jdbc.sql("INSERT INTO maksut.veloitus VALUES (?, ?)")
            .params(v.korrelaatio(), summa).update();
        return new Vastaus("MAKSETTU", "{}");
    }
}
