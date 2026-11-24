package fi.tutoriaalit.kauppa.tilaus;

import fi.tutoriaalit.kauppa.KauppaAsetukset;
import fi.tutoriaalit.kauppa.tuote.Tuote;
import fi.tutoriaalit.kauppa.tuote.TuoteRepository;
import fi.tutoriaalit.kauppa.virheet.EiLoydy;
import fi.tutoriaalit.kauppa.virheet.VirheellinenPyynto;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import java.time.Clock;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.security.access.prepost.PostAuthorize;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class TilausPalvelu {

    /** Asiakkaan pyytämä rivi: tuote ja määrä. */
    public record Rivi(long tuoteId, int maara) {
    }

    private static final Logger LOKI =
            LoggerFactory.getLogger(TilausPalvelu.class);

    private final TilausRepository tilaukset;
    private final TuoteRepository tuotteet;
    private final Varasto varasto;
    private final JdbcClient jdbc;
    private final KauppaAsetukset asetukset;
    private final Clock kello;
    private final Counter luodut;

    public TilausPalvelu(TilausRepository tilaukset, TuoteRepository tuotteet,
            Varasto varasto, JdbcClient jdbc, KauppaAsetukset asetukset,
            Clock kello, MeterRegistry mittarit) {
        this.tilaukset = tilaukset;
        this.tuotteet = tuotteet;
        this.varasto = varasto;
        this.jdbc = jdbc;
        this.asetukset = asetukset;
        this.kello = kello;
        // @alku mittari
        this.luodut = Counter.builder("kauppa.tilaukset")
                .description("luodut tilaukset")
                .register(mittarit);
        // @loppu mittari
    }

    // @alku luo
    /**
     * Luo tilauksen yhdessä transaktiossa: idempotenssiavain, saldojen
     * varaus ja tilaus onnistuvat tai peruuntuvat yhdessä.
     */
    @Transactional
    public Tilaus luo(String asiakas, String avain, List<Rivi> pyydetyt) {
        if (pyydetyt.size() > asetukset.maksimirivit()) {
            throw new VirheellinenPyynto("liikaa rivejä");
        }
        if (avain != null) {
            // Ensin: kaksi samanaikaista toistoa törmäävät pääavaimeen.
            jdbc.sql("""
                    INSERT INTO idempotenssi (asiakas, avain)
                    VALUES (:asiakas, :avain)
                    """)
                    .param("asiakas", asiakas).param("avain", avain)
                    .update();
        }
        List<TilausRivi> rivit = new ArrayList<>();
        for (Rivi r : pyydetyt) {
            Tuote t = tuotteet.findById(r.tuoteId())
                    .orElseThrow(() -> new EiLoydy("tuote", r.tuoteId()));
            varasto.varaa(t.id(), r.maara());   // voi heittää: kaikki peruu
            rivit.add(new TilausRivi(t.id(), r.maara(), t.hintaSentteina()));
        }
        Tilaus tilaus = tilaukset.save(
                new Tilaus(null, asiakas, Instant.now(kello), rivit));
        if (avain != null) {
            jdbc.sql("""
                    UPDATE idempotenssi SET tilaus_id = :tilaus
                     WHERE asiakas = :asiakas AND avain = :avain
                    """)
                    .param("tilaus", tilaus.id())
                    .param("asiakas", asiakas).param("avain", avain)
                    .update();
        }
        luodut.increment();
        LOKI.info("tilaus {} luotu, {} riviä", tilaus.id(), rivit.size());
        return tilaus;
    }
    // @loppu luo

    // @alku toisto
    /** Aiemmin samalla avaimella luotu tilaus, jos sellainen on. */
    @Transactional(readOnly = true)
    public Optional<Tilaus> haeAvaimella(String asiakas, String avain) {
        return jdbc.sql("""
                SELECT tilaus_id FROM idempotenssi
                 WHERE asiakas = :asiakas AND avain = :avain
                """)
                .param("asiakas", asiakas).param("avain", avain)
                .query(Long.class)
                .optional()
                .flatMap(tilaukset::findById);
    }
    // @loppu toisto

    // @alku valtuutus
    /** Tilauksen näkee sen tehnyt asiakas ja ylläpitäjä. */
    @Transactional(readOnly = true)
    @PostAuthorize("returnObject.asiakas() == authentication.name"
            + " or hasRole('YLLAPITAJA')")
    public Tilaus hae(long id) {
        return tilaukset.findById(id)
                .orElseThrow(() -> new EiLoydy("tilaus", id));
    }
    // @loppu valtuutus

    @Transactional(readOnly = true)
    public List<Tilaus> asiakkaan(String asiakas) {
        return tilaukset.findByAsiakasOrderByIdDesc(asiakas);
    }
}
