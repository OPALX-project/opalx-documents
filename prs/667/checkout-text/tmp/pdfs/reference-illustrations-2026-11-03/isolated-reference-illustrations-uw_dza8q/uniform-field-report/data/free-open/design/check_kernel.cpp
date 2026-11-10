#include "SpaceCharge/FFT2D5/FFT2D5FreeSpaceKernel.h"
#include <iomanip>
#include <iostream>
int main() {
    int kind;
    double x,y,s,hx,hy,hs,kappa,gamma;
    std::cout << std::setprecision(17);
    while (std::cin >> kind >> x >> y >> s >> hx >> hy >> hs >> kappa >> gamma) {
        std::cout << opalx::spacecharge::fft2d5_free::CellKernel::average(
                kind,x,y,s,hx,hy,hs,kappa,gamma) << '\n';
    }
}
