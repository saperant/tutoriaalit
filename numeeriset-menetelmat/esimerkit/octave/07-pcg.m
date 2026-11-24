% Harva matriisi ja liittogradientti Octavella.
m = 100;
e = ones(m, 1);
T = spdiags([-e 2*e -e], -1:1, m, m);
A = kron(speye(m), T) + kron(T, speye(m));   % 2D-Poisson, n = 10 000
printf("n = %d, nollasta poikkeavia %d\n", rows(A), nnz(A));
b = ones(rows(A), 1) / 101^2;
[x, lippu, jaannos, kierroksia] = pcg(A, b, 1e-8, 1000);
printf("pcg: lippu %d, alle 400 kierrosta: %d\n", lippu, kierroksia < 400);
% Esiehdoste: epätäydellinen Cholesky vähentää kierroksia.
L = ichol(A);
[x2, lippu2, ~, kierroksia2] = pcg(A, b, 1e-8, 1000, L, L');
printf("ichol-esiehdosteella vähemmän kierroksia: %d\n", ...
       kierroksia2 < kierroksia);
printf("suurin taipuma %.5f\n", max(x2));
