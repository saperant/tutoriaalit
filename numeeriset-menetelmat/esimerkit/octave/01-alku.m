% Sama e^-20 -koe Octavella. Vektorit ja alkioittaiset operaattorit
% (.^ ./) korvaavat silmukan.
k = 0:149;
termit = (-20) .^ k ./ factorial(k);
suora = sum(termit);
kaanteinen = 1 / sum(20 .^ k ./ factorial(k));
tarkka = exp(-20);
printf("suora sarja    %.6e\n", suora);
printf("1 / sarja(20)  %.6e\n", kaanteinen);
printf("exp(-20)       %.6e\n", tarkka);
printf("eps = %.3e\n", eps);
