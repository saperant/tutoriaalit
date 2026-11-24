package fi.tutoriaalit.palvelut.kauppa.varasto.sisainen;

import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.stereotype.Repository;

@Repository
public class SaldoTaulu {
    private final JdbcClient jdbc;

    SaldoTaulu(JdbcClient jdbc) {
        this.jdbc = jdbc;
    }

    public int saldo(String tuote) {
        return jdbc.sql("SELECT saldo FROM varasto_saldo WHERE tuote = ?")
            .param(tuote).query(Integer.class).single();
    }

    /** Vähentää saldoa, jos sitä on tarpeeksi. Palauttaa onnistuiko. */
    public boolean vahenna(String tuote, int maara) {
        return jdbc.sql("""
                UPDATE varasto_saldo SET saldo = saldo - :maara
                WHERE tuote = :tuote AND saldo >= :maara""")
            .param("tuote", tuote).param("maara", maara)
            .update() == 1;
    }
}
