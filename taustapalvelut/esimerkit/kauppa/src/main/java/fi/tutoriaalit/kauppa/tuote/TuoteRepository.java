package fi.tutoriaalit.kauppa.tuote;

import java.util.Optional;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.repository.ListCrudRepository;
import org.springframework.data.repository.PagingAndSortingRepository;

// @alku repository
/** Spring Data luo toteutuksen rajapinnan metodien nimistä. */
public interface TuoteRepository extends ListCrudRepository<Tuote, Long>,
        PagingAndSortingRepository<Tuote, Long> {

    Optional<Tuote> findByNimi(String nimi);

    Page<Tuote> findBySaldoGreaterThan(int saldo, Pageable sivu);
}
// @loppu repository
