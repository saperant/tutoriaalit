package fi.tutoriaalit.kauppa.tilaus;

import jakarta.validation.Valid;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotEmpty;
import java.net.URI;
import java.security.Principal;
import java.util.List;
import org.springframework.dao.DuplicateKeyException;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/tilaukset")
public class TilausOhjain {

    public record RiviPyynto(@Min(1) long tuoteId,
            @Min(1) @Max(1000) int maara) {
    }

    public record TilausPyynto(@NotEmpty List<@Valid RiviPyynto> rivit) {
    }

    public record TilausVastaus(long id, String asiakas,
            List<TilausRivi> rivit, long summaSentteina) {
        static TilausVastaus tilauksesta(Tilaus t) {
            return new TilausVastaus(t.id(), t.asiakas(), t.rivit(),
                    t.summaSentteina());
        }
    }

    private final TilausPalvelu palvelu;

    public TilausOhjain(TilausPalvelu palvelu) {
        this.palvelu = palvelu;
    }

    // @alku luonti
    @PostMapping
    public ResponseEntity<TilausVastaus> luo(
            @Valid @RequestBody TilausPyynto pyynto,
            @RequestHeader(name = "Idempotency-Key", required = false)
            String avain,
            Principal kayttaja) {
        List<TilausPalvelu.Rivi> rivit = pyynto.rivit().stream()
                .map(r -> new TilausPalvelu.Rivi(r.tuoteId(), r.maara()))
                .toList();
        Tilaus tilaus;
        try {
            tilaus = avain == null ? null
                    : palvelu.haeAvaimella(kayttaja.getName(), avain)
                            .orElse(null);
            if (tilaus == null) {
                tilaus = palvelu.luo(kayttaja.getName(), avain, rivit);
            }
        } catch (DuplicateKeyException samanaikainen) {
            // Sama avain käsiteltiin juuri toisessa pyynnössä.
            tilaus = palvelu.haeAvaimella(kayttaja.getName(), avain)
                    .orElseThrow();
        }
        return ResponseEntity
                .created(URI.create("/api/v1/tilaukset/" + tilaus.id()))
                .body(TilausVastaus.tilauksesta(tilaus));
    }
    // @loppu luonti

    @GetMapping("/{id}")
    public TilausVastaus hae(@PathVariable long id) {
        return TilausVastaus.tilauksesta(palvelu.hae(id));
    }

    @GetMapping
    public List<TilausVastaus> omat(Principal kayttaja) {
        return palvelu.asiakkaan(kayttaja.getName()).stream()
                .map(TilausVastaus::tilauksesta)
                .toList();
    }
}
