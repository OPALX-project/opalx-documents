#include <fftw3.h>
#include <algorithm>
#include <cmath>
#include <iostream>
int main() {
    std::cout << "default_planner_threads=" << fftw_planner_nthreads() << '\n';
    if (!fftw_init_threads()) return 1;
    constexpr int n=128, count=n*n;
    auto* real=fftw_alloc_real(count);
    auto* spec=fftw_alloc_complex(n*(n/2+1));
    if (!real || !spec) return 2;
    for (int threads : {1,4,16}) {
        fftw_plan_with_nthreads(threads);
        auto forward=fftw_plan_dft_r2c_2d(n,n,real,spec,FFTW_ESTIMATE);
        auto backward=fftw_plan_dft_c2r_2d(n,n,spec,real,FFTW_ESTIMATE);
        if (!forward || !backward) return 3;
        for(int i=0;i<count;++i) real[i]=std::sin(.1*i)+.3*std::cos(.7*i);
        fftw_execute(forward); fftw_execute(backward);
        double error=0.;
        for(int i=0;i<count;++i) error=std::max(error,std::abs(real[i]/count-(std::sin(.1*i)+.3*std::cos(.7*i))));
        std::cout << "requested_max_threads=" << threads << " planner_threads=" << fftw_planner_nthreads() << " roundtrip_max_error=" << error << '\n';
        if (error>1e-12 || fftw_planner_nthreads()!=threads) return 4;
        fftw_destroy_plan(forward); fftw_destroy_plan(backward);
    }
    fftw_free(real); fftw_free(spec); fftw_cleanup_threads();
}
