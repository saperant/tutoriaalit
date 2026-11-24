package fi.tutoriaalit.kauppa.raportti;

import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/raportit")
public class RaporttiOhjain {

    private final MyyntiRaportti raportti;

    public RaporttiOhjain(MyyntiRaportti raportti) {
        this.raportti = raportti;
    }

    @GetMapping("/myynti")
    public List<MyyntiRaportti.Myynti> myynti(
            @RequestParam(defaultValue = "5") int montako) {
        return raportti.parhaat(Math.clamp(montako, 1, 50));
    }
}
