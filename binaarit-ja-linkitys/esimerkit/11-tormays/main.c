void lataa_kuva(const char *nimi);
void lataa_aani(const char *nimi);

int main(void)
{
    lataa_kuva("logo.png");
    lataa_aani("piip.wav");
    return 0;
}
