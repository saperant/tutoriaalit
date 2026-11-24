"""Neo4j ja Cypher: seuraajat, suositukset ja lyhin polku."""

from nosql.kontit import Ymparisto, aja
from nosql.verkosto import OSTI, SEURAA


def ajo(ymp: Ymparisto) -> None:
    ajuri = ymp.neo4j()
    ajuri.execute_query("MATCH (n) DETACH DELETE n")

    # @alku luonti
    ajuri.execute_query("""
        UNWIND $seuraa AS pari
        MERGE (a:Kayttaja {nimi: pari[0]})
        MERGE (b:Kayttaja {nimi: pari[1]})
        MERGE (a)-[:SEURAA]->(b)""", seuraa=SEURAA)
    ajuri.execute_query("""
        UNWIND $osti AS pari
        MATCH (k:Kayttaja {nimi: pari[0]})
        MERGE (t:Tuote {nimi: pari[1]})
        MERGE (k)-[:OSTI]->(t)""", osti=OSTI)
    # @loppu luonti

    # @alku kaksi-askelta
    tulos = ajuri.execute_query("""
        MATCH (a:Kayttaja {nimi: 'aino'})-[:SEURAA*2]->(b:Kayttaja)
        WHERE b <> a AND NOT (a)-[:SEURAA]->(b)
        RETURN DISTINCT b.nimi AS nimi ORDER BY nimi""")
    print("ainon kaukaiset:", [r["nimi"] for r in tulos.records])
    # @loppu kaksi-askelta

    # @alku suositus
    tulos = ajuri.execute_query("""
        MATCH (t:Tuote {nimi: 'keitin'})<-[:OSTI]-(k)-[:OSTI]->(muu)
        WHERE muu <> t
        RETURN muu.nimi AS tuote, count(DISTINCT k) AS ostajia
        ORDER BY ostajia DESC, tuote""")
    for r in tulos.records:
        print("keittimen ostajat ostivat myos:", r["tuote"], r["ostajia"])
    # @loppu suositus

    # @alku polku
    tulos = ajuri.execute_query("""
        MATCH p = shortestPath(
            (a:Kayttaja {nimi: 'aino'})-[:SEURAA*]->
            (b:Kayttaja {nimi: 'pekka'}))
        RETURN [n IN nodes(p) | n.nimi] AS polku""")
    print("lyhin polku:", " -> ".join(tulos.records[0]["polku"]))
    # @loppu polku


if __name__ == "__main__":
    aja(ajo)
