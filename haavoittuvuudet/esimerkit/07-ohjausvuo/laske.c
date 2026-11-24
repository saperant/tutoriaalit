/* Pieni funktio, jonka konekielestä katsotaan ohjausvuon suojausten
 * lisäämät käskyt. */
int skaalaa(int (*muunnos)(int), int arvo)
{
    return muunnos(arvo) * 2;
}
