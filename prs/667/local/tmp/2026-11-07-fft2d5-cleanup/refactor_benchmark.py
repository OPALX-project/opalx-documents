from pathlib import Path
p=Path('unit_tests/SpaceCharge/BenchmarkFFT2D5Batch.cpp');s=p.read_text();a=s.index('        void solve(');b=s.index('    struct Problem {',a);old=s[a:b]
def phase(name,nextname=None):
 i=old.index('                phase("'+name+'"');j=old.index('                phase("'+nextname+'"',i) if nextname else old.rfind('            }')
 return old[i:j]
pack=phase('2D5 Pack','2D5 FFT Rho');forward=phase('2D5 FFT Rho','2D5 Convolution');mult=phase('2D5 Convolution','2D5 FFT Back');back=phase('2D5 FFT Back','2D5 Field');field=phase('2D5 Field')
new='''        /** @brief Clear outputs, stage occupied IDs and execute each bounded candidate batch. */
        void solve(const P::ScalarField3_t& density, P::VectorField3_t& electric,
                   std::span<const size_t> occupied, double coupling, P::ScalarField3_t* potential) {
            Kokkos::deep_copy(electric.getView(), P::Vector3_t(0.));
            if (potential) Kokkos::deep_copy(potential->getView(), 0.);
            if (occupied.empty()) return;
            if (slices.extent(0) < occupied.size()) slices = IV("benchmarkSlices", occupied.size());
            auto host = Kokkos::create_mirror_view(slices);
            for (size_t i = 0; i < occupied.size(); ++i) host(i) = occupied[i];
            Kokkos::deep_copy(slices, host);
            for (size_t first = 0; first < occupied.size(); first += capacity) {
                const int count = static_cast<int>(std::min(size_t(capacity), occupied.size()-first));
                plan(count);
                pack(density, first, count, coupling);
                transformForward(count);
                convolve(count);
                transformBackward(count);
                extractFields(electric, potential, first, count);
            }
        }
        /** @brief Pack source planes with the candidate's real or full-complex layout. */
        void pack(const P::ScalarField3_t& density, size_t first, int count, double coupling) {
            const auto source = density.getView();
            const int sg = density.getNghost();
            auto r = real; auto f = full; auto ids = slices;
            const size_t x=nx,y=ny,xx=nx2,yy=ny2,rr=nr;
            const bool complex = mode == MergedC2C;
'''+pack+'''        }
        /** @brief Apply the selected forward executor pipeline to count planes. */
        void transformForward(int count) {
            auto& p = plan(count);
            auto s=spectrum,c=columns;
            const size_t cc=nc,cx=ncx,yy=ny2;
'''+forward+'''        }
        /** @brief Multiply candidate spectra by the matching layout of normalized Green. */
        void convolve(int count) {
            auto s=spectrum,c=columns,f=full;
            auto gr=greenRow,gc=greenColumn,gf=greenFull;
            const size_t rr=nr,cc=nc;
            const double scale=area;
'''+mult+'''        }
        /** @brief Reverse the selected executor pipeline without changing its scaling. */
        void transformBackward(int count) {
            auto& p=plan(count);
            auto s=spectrum,c=columns;
            const size_t cc=nc,cx=ncx,yy=ny2;
'''+back+'''        }
        /** @brief Extract all transverse fields and optional wrapped potential halos for checks. */
        void extractFields(P::VectorField3_t& electric, P::ScalarField3_t* potential,
                           size_t first,int count) {
            auto e=electric.getView(); const int eg=electric.getNghost();
            auto r=real; auto f=full; auto ids=slices;
            const size_t x=nx,y=ny,xx=nx2,yy=ny2,rr=nr;
            const bool complex=mode==MergedC2C;
            const double idx=inv2dx,idy=inv2dy;
'''+field+'''        }
    };

''';s=s[:a]+new+s[b:]
# Pull independent validation and timed sweeps out of the entry point.
a=s.index('    void run(bool validateOnly, bool quick)');b=s.index('}  // namespace',a);old=s[a:b]
validation=old[old.index('        for (auto shape'):old.index('        if (validateOnly) return;')]
inner=old[old.index('                p.reference(batch);'):old.index('                // Retained implementations')]
time=old[old.index('                // Retained implementations'):old.index('                for (auto& c : candidates) {',old.index('                // Retained implementations'))]
end=old[old.index('                for (auto& c : candidates) {',old.index('                // Retained implementations')):old.index('                std::cout << "COMPLETE')]
new='''    /** @brief Return candidate modes; the known-invalid no-reorder multi-batch mode is gated by callers. */
    std::vector<Mode> benchmarkModes() {
        return {PublicReorder, PublicNoReorder, RowsTranspose, MergedC2C};
    }
    /** @brief Validate fields and potential halos on rectangular dense/sparse/empty cases. */
    void validateCandidates(std::ostream& checks) {
        const auto modes=benchmarkModes();
'''+validation+'''    }
    /** @brief Warm all candidates, then alternate synchronized timing order across rounds. */
    void timeCandidates(Problem& p,int batch,std::vector<std::unique_ptr<Candidate>>& candidates,
                        const std::vector<Mode>& selected,std::ofstream& times,bool quick) {
        const int nz=p.nz;
'''+time+'''    }
    /** @brief Validate and time one physical grid and batch size, retaining final checks. */
    void measureProblem(Problem& p,int batch,std::ostream& checks,std::ofstream& times,bool quick) {
        const int nz=p.nz;
        const auto modes=benchmarkModes();
'''+inner+'''        timeCandidates(p,batch,candidates,selected,times,quick);
'''+end+'''        std::cout << "COMPLETE nz=" << nz << " batch=" << batch << std::endl;
    }
    /** @brief Write validation tables and, unless validateOnly, a bounded or full timing sweep.
     * @param validateOnly Suppress timing cases. @param quick Reduce physical-grid timing rounds. */
    void run(bool validateOnly, bool quick) {
        std::ofstream checks("validation.csv"), times("samples.csv");
        checks << std::setprecision(17); times << std::setprecision(17);
        checks << "method,nx,ny,nz,batch,source_case,occupied,relative_E_error,relative_phi_error\\n";
        times << "method,nx,ny,nz,batch,round,seconds_per_solve\\n";
        validateCandidates(checks);
        if (validateOnly) return;
        for(int nz : (quick ? std::vector<int>{256} : std::vector<int>{256,512})) {
            Problem p(64,64,nz); p.fill(0);
            for(int batch : (quick ? std::vector<int>{64} : std::vector<int>{1,8,32,64}))
                measureProblem(p,batch,checks,times,quick);
        }
    }
''';s=s[:a]+new+s[b:]
# Brief contracts for the remaining small benchmark helpers.
for signature,doc in [
('    Policy range(', 'Construct a zero-based three-dimensional iteration range; arguments are extents.'),
('    Stream stream()', 'Return the default CUDA stream, or the host backend null stream.'),
('    Box box(', 'Construct a zero-based heFFTe box; all three arguments are positive extents.'),
('    std::complex<double>* ptr(', 'Expose Kokkos complex storage through the verified native complex ABI.'),
('    const char* label(', 'Return the stable CSV name of a backend candidate.'),
('        Plans(', 'Create executor plans and scratch for one candidate and actual plane count.'),
('        Candidate(', 'Allocate a bounded candidate layout and copy the normalized reference Green spectrum.'),
('        void initializeGreen(', 'Materialize row, column and full-complex Green layouts for equivalent candidate checks.'),
('        static void phase(', 'Time completed work with the same explicit inner fence as production phases.'),
('        Plans& plan(', 'Return or create plans cached for the actual batch size.'),
('        Problem(', 'Allocate a rectangular source, native reference solver and independent result fields.'),
('        void fill(', 'Fill a deterministic dense, neutral/sparse or empty source and record occupied planes.'),
('        void reference(', 'Compute the native reference and retain source density for unchanged-input checks.'),
('        std::pair<double, double> check()', 'Compare every field and potential halo to the reference and reject nonfinite or excessive errors.'),
('    double measure(', 'Measure mean synchronized runtime over the requested positive repeat count.'),
('int main(', 'Run a one-rank backend benchmark; report validation or setup failures with nonzero status.')]:
 if signature in s:s=s.replace(signature,('        ' if signature.startswith('        ') else '    ' if signature.startswith('    ') else '')+'/** @brief '+doc+' */\n'+signature,1)
p.write_text(s)
