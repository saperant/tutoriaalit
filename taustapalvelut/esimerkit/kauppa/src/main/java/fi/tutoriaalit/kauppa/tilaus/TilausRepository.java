package fi.tutoriaalit.kauppa.tilaus;

import java.util.List;
import org.springframework.data.repository.ListCrudRepository;

public interface TilausRepository extends ListCrudRepository<Tilaus, Long> {

    List<Tilaus> findByAsiakasOrderByIdDesc(String asiakas);
}
