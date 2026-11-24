% Numeerinen integrointi Octavella.
x = linspace(0, 1, 33);
printf("trapz, 33 pistettä:  virhe %.1e\n", abs(trapz(x, exp(x)) - (e - 1)));
virhe = abs(integral(@(x) exp(x), 0, 1) - (e - 1));
printf("integral:            virhe alle 1e-14: %d\n", virhe < 1e-14);
% quadgk kestää päätepisteen singulariteetin.
[q, arvio] = quadgk(@(x) 1 ./ sqrt(x), 0, 1);
printf("quadgk 1/sqrt(x):    %.10f\n", q);
