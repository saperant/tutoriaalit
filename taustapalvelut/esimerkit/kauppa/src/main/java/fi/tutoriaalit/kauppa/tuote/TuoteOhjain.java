package fi.tutoriaalit.kauppa.tuote;

import fi.tutoriaalit.kauppa.KauppaAsetukset;
import jakarta.validation.Valid;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.PositiveOrZero;
import jakarta.validation.constraints.Size;
import java.net.URI;
import java.util.List;
import org.springframework.data.domain.Page;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.context.request.WebRequest;

/** Tuotteiden REST-rajapinta. Ohjain kääntää HTTP:n palvelukutsuiksi. */
@RestController
@RequestMapping("/api/v1/tuotteet")
public class TuoteOhjain {

    // @alku dto
    /** Rajapinnan esitysmuoto: erillään tietokantarakenteesta. */
    public record TuoteVastaus(long id, String nimi, long hintaSentteina,
            int saldo) {
        static TuoteVastaus tuotteesta(Tuote t) {
            return new TuoteVastaus(t.id(), t.nimi(), t.hintaSentteina(),
                    t.saldo());
        }
    }

    public record TuoteSivu(List<TuoteVastaus> tuotteet, int sivu,
            int koko, long yhteensa) {
    }

    /** Pyynnön runko validoidaan ennen kuin se pääsee palveluun. */
    public record UusiTuote(
            @NotBlank @Size(max = 100) String nimi,
            @PositiveOrZero long hintaSentteina,
            @Min(0) @Max(1_000_000) int saldo) {
    }

    public record HinnanMuutos(@PositiveOrZero long hintaSentteina) {
    }
    // @loppu dto

    private final TuotePalvelu palvelu;
    private final KauppaAsetukset asetukset;

    public TuoteOhjain(TuotePalvelu palvelu, KauppaAsetukset asetukset) {
        this.palvelu = palvelu;
        this.asetukset = asetukset;
    }

    // @alku listaus
    @GetMapping
    public TuoteSivu listaa(
            @RequestParam(defaultValue = "0") @Min(0) int sivu,
            @RequestParam(defaultValue = "20") @Min(1) int koko) {
        int rajattu = Math.min(koko, asetukset.sivunEnimmaiskoko());
        Page<Tuote> tulos = palvelu.sivu(sivu, rajattu);
        return new TuoteSivu(
                tulos.map(TuoteVastaus::tuotteesta).getContent(),
                sivu, rajattu, tulos.getTotalElements());
    }
    // @loppu listaus

    // @alku haku
    @GetMapping("/{id}")
    public ResponseEntity<TuoteVastaus> hae(@PathVariable long id,
            WebRequest pyynto) {
        Tuote t = palvelu.hae(id);
        String etag = "\"" + t.versio() + "\"";
        if (pyynto.checkNotModified(etag)) {
            return null;                    // Spring vastaa 304
        }
        return ResponseEntity.ok().eTag(etag)
                .body(TuoteVastaus.tuotteesta(t));
    }
    // @loppu haku

    // @alku lisays
    @PostMapping
    public ResponseEntity<TuoteVastaus> lisaa(
            @Valid @RequestBody UusiTuote uusi) {
        Tuote t = palvelu.lisaa(uusi.nimi(), uusi.hintaSentteina(),
                uusi.saldo());
        URI sijainti = URI.create("/api/v1/tuotteet/" + t.id());
        return ResponseEntity.created(sijainti)
                .eTag("\"" + t.versio() + "\"")
                .body(TuoteVastaus.tuotteesta(t));
    }
    // @loppu lisays

    // @alku hinta
    @PutMapping("/{id}/hinta")
    public ResponseEntity<TuoteVastaus> muutaHinta(@PathVariable long id,
            @RequestHeader(name = "If-Match", required = false) String ehto,
            @Valid @RequestBody HinnanMuutos muutos) {
        if (ehto == null) {
            // Ilman versiota muutos voisi kumota toisen tekemän muutoksen.
            return ResponseEntity.status(HttpStatus.PRECONDITION_REQUIRED)
                    .build();
        }
        long versio = Long.parseLong(ehto.replace("\"", ""));
        Tuote t = palvelu.muutaHinta(id, versio, muutos.hintaSentteina());
        return ResponseEntity.ok().eTag("\"" + t.versio() + "\"")
                .body(TuoteVastaus.tuotteesta(t));
    }
    // @loppu hinta
}
