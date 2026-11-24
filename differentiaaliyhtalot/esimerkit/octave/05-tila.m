% Tilaesitys Octavella: ominaisarvot ja matriisieksponentti.
1;

# @alku tila
A = [0 1; -4 -5];
[V, D] = eig(A);
printf("ominaisarvot: %g %g\n", sort(diag(D)));
x = expm(A * 1.5) * [1; 0];
printf("y(1,5) = %.10f\n", x(1));
printf("tarkka   %.10f\n", 4/3 * exp(-1.5) - 1/3 * exp(-6));
# @loppu tila
