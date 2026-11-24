% Lineaariset yhtälöryhmät Octavella: \ valitsee menetelmän itse.
A = [2 1 1; 4 -6 0; -2 7 2];
b = [5; -2; 9];
x = A \ b;                            % neliömatriisi: LU tuennalla
printf("x = [%g %g %g]\n", x);
[L, U, P] = lu(A);                    % P*A = L*U
printf("norm(P*A - L*U) < 1e-14: %d\n", norm(P*A - L*U) < 1e-14);

S = [4 2; 2 3];                       % symmetrinen ja PD
R = chol(S);                          % S = R' * R, R yläkolmio
printf("chol: R = [%g %g; %g %g]\n", R');

H = hilb(10);
y = H \ (H * ones(10, 1));
printf("hilb(10): cond %.0e, virhe < 1e-6: %d\n", cond(H), ...
       norm(y - 1) < 1e-6);
