package fi.tutoriaalit.palveluturva.palvelu;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.*;

@SpringBootApplication
@ConfigurationPropertiesScan
public class Laskupalvelu {
    public static void main(String[] args) {
        SpringApplication.run(Laskupalvelu.class, args);
    }
}
