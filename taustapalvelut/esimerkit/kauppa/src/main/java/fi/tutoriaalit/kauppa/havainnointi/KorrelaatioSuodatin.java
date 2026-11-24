package fi.tutoriaalit.kauppa.havainnointi;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.UUID;
import java.util.regex.Pattern;
import org.slf4j.MDC;
import org.springframework.core.Ordered;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

// @alku suodatin
/**
 * Antaa jokaiselle pyynnölle korrelaatiotunnuksen. Tunnus kulkee
 * lokiriveillä (MDC) ja vastausotsakkeessa, joten yhden pyynnön kaikki
 * lokirivit löytyvät, myös palvelusta toiseen, jos kutsuja välittää
 * sen.
 */
@Component
@Order(Ordered.HIGHEST_PRECEDENCE)
public class KorrelaatioSuodatin extends OncePerRequestFilter {

    public static final String OTSAKE = "X-Correlation-Id";
    private static final Pattern KELPO = Pattern.compile("[\\w-]{1,64}");

    @Override
    protected void doFilterInternal(HttpServletRequest pyynto,
            HttpServletResponse vastaus, FilterChain ketju)
            throws ServletException, IOException {
        String tunnus = pyynto.getHeader(OTSAKE);
        if (tunnus == null || !KELPO.matcher(tunnus).matches()) {
            tunnus = UUID.randomUUID().toString();  // ei luoteta syötteeseen
        }
        MDC.put("korrelaatio", tunnus);
        vastaus.setHeader(OTSAKE, tunnus);
        try {
            ketju.doFilter(pyynto, vastaus);
        } finally {
            MDC.remove("korrelaatio");   // säie palaa altaaseen
        }
    }
}
// @loppu suodatin
