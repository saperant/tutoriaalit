package fi.tutoriaalit.palvelut.viestit;

import jakarta.jms.ConnectionFactory;
import org.apache.activemq.artemis.api.core.SimpleString;
import org.apache.activemq.artemis.core.settings.impl.AddressSettings;
// Tähtituonti pitää rivit PDF:n levyisinä.
import org.springframework.boot.artemis.autoconfigure.*;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;
import org.springframework.jms.config.DefaultJmsListenerContainerFactory;
import org.springframework.jms.core.JmsTemplate;

@Configuration
class Viestinvalitys {

    // @alku dlq
    /** Välittäjä yrittää viestiä kolmesti; sitten se siirtyy
     *  kuolleiden kirjeiden jonoon (dead letter queue). */
    @Bean
    ArtemisConfigurationCustomizer kuolleetKirjeet() {
        return asetukset -> asetukset.addAddressSetting("#",
            new AddressSettings()
                .setMaxDeliveryAttempts(3)
                .setDeadLetterAddress(SimpleString.of("DLQ")));
    }
    // @loppu dlq

    // @alku kuuntelijat
    /** Jonot (point-to-point): yksi vastaanottaja per viesti. Istunto on
     *  transaktionaalinen: jos käsittely heittää poikkeuksen, viesti
     *  palaa jonoon ja toimitetaan uudelleen. */
    @Bean
    DefaultJmsListenerContainerFactory jonot(ConnectionFactory yhteydet) {
        return tehdas(yhteydet, false);
    }

    /** Aiheet (julkaise–tilaa): jokainen tilaaja saa oman kopion. */
    @Bean
    DefaultJmsListenerContainerFactory aiheet(ConnectionFactory yhteydet) {
        return tehdas(yhteydet, true);
    }

    private static DefaultJmsListenerContainerFactory tehdas(
            ConnectionFactory yhteydet, boolean aiheet) {
        var tehdas = new DefaultJmsListenerContainerFactory();
        tehdas.setConnectionFactory(yhteydet);
        tehdas.setSessionTransacted(true);
        tehdas.setPubSubDomain(aiheet);
        return tehdas;
    }
    // @loppu kuuntelijat

    @Bean
    @Primary
    JmsTemplate jmsTemplate(ConnectionFactory yhteydet) {
        return new JmsTemplate(yhteydet);
    }

    @Bean
    JmsTemplate aiheTemplate(ConnectionFactory yhteydet) {
        var template = new JmsTemplate(yhteydet);
        template.setPubSubDomain(true);
        return template;
    }
}
