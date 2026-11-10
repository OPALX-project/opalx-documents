from pathlib import Path
p=Path('src/SpaceCharge/FFT2D5/FFT2D5Poisson.cpp');s=p.read_text();start=s.index('void FFT2D5Poisson::solveBatched(');old=s[start:]
def chunk(a,b):return old[old.index(a):old.index(b)]
validation=chunk('    if (batchSize <= 0)','    const auto field = electric.getView();').replace('            batchPlan_m.reset();','            batchCapacity_m = 0;')
allocation=chunk('    if (!batchPlan_m','    if (batchSlices_m.extent')
allocation=allocation.replace('!batchPlan_m || ','batchReal_m.extent(0) == 0 || ')
allocation=allocation.replace('            batchPlan_m = std::make_unique<BatchPlan>(\n                    inbox, outbox, 0, MPI_COMM_SELF,\n                    ippl::fft::makeHeffteOptions<BatchBackend::backend_t>(params_m));','''            batchPlan_m.reset();
            batchWorkspace_m = BatchWorkspace{};
            if (ippl::Comm->size() > 1) {
                batchPlan_m = std::make_unique<BatchPlan>(
                        inbox, outbox, 0, MPI_COMM_SELF,
                        ippl::fft::makeHeffteOptions<BatchBackend::backend_t>(params_m));
                batchWorkspace_m = BatchWorkspace(batchPlan_m->size_workspace());
            }''').replace('            batchWorkspace_m  = BatchWorkspace(batchPlan_m->size_workspace() * capacity);\n','')
slices=chunk('    if (batchSlices_m.extent','    const auto green = batchGreen_m;')
green=chunk('    const auto green = batchGreen_m;','    const auto source   = density.getView();')
rows=chunk('        if (!batchXRows_m.contains(count))','        auto& xRows = *batchXRows_m.at(count);');rows='\n'.join(x[4:] if x.startswith('    ') else x for x in rows.splitlines())+'\n';rows=rows.replace('it->first != capacity','it->first != batchCapacity_m')
pack=chunk('        timedPhase("2D5 Pack"','        timedPhase("2D5 FFT Rho"')
fftforward=chunk('            xRows.forward(real.data()','        timedPhase("2D5 Convolution"');fftforward=fftforward[:fftforward.rfind('        });')]
mult=chunk('        timedPhase("2D5 Convolution"','        timedPhase("2D5 FFT Back"')
fftback=chunk('            yRows.backward(columnData','        timedPhase("2D5 Field"');fftback=fftback[:fftback.rfind('        });')]
field=old[old.index('        timedPhase("2D5 Field"'):];field=field[:field.rfind('    }')]
# Local view bindings retain the same expressions and arithmetic as the original body.
real='''    const auto real = batchReal_m;
    const auto nx2 = nx2_, ny2 = ny2_;
    const size_t nr = nx2 * ny2;
'''
spectrum='''    const auto real = batchReal_m, spectrum = batchSpectrum_m;
    const auto columns = batchColumns_m;
    const auto nx2 = nx2_, ny2 = ny2_;
    const size_t ncx = nx2 / 2 + 1, nc = ncx * ny2;
    auto& xRows = *batchXRows_m.at(count);
    auto& yRows = *batchYRows_m.at(count);
    static_assert(sizeof(Complex) == sizeof(std::complex<double>));
    auto* rowData = reinterpret_cast<std::complex<double>*>(spectrum.data());
    auto* columnData = reinterpret_cast<std::complex<double>*>(columns.data());
    auto* scratch = reinterpret_cast<std::complex<double>*>(batchRowScratch_m.data());
'''
new='''void FFT2D5Poisson::solveBatched(
        const ScalarField3_t& density, VectorField3_t& electric, std::span<const size_t> occupied,
        int batchSize, double coupling, ScalarField3_t* potential) {
    const int capacity = validateBatchGeometry(density, occupied, batchSize);
    Kokkos::deep_copy(electric.getView(), Vector3_t(0.));
    if (potential) Kokkos::deep_copy(potential->getView(), 0.);
    if (occupied.empty()) return;
    prepareBatchBuffers(capacity);
    copyOccupiedSlices(occupied);
    prepareBatchGreen();
    for (size_t first = 0; first < occupied.size(); first += capacity) {
        const int count = static_cast<int>(std::min(size_t(capacity), occupied.size() - first));
        prepareRowExecutors(count);
        packBatch(density, first, count, coupling);
        transformBatch(count, true);
        multiplyBatchGreen(count);
        transformBatch(count, false);
        extractBatchFields(electric, potential, first, count);
    }
}

int FFT2D5Poisson::validateBatchGeometry(
        const ScalarField3_t& density, std::span<const size_t> occupied, int batchSize) {
'''+validation+'''    return static_cast<int>(std::min(size_t(batchSize), nz));
}

void FFT2D5Poisson::prepareBatchBuffers(int capacity) {
    const size_t nr = nx2_ * ny2_, ncx = nx2_ / 2 + 1, nc = ncx * ny2_;
'''+allocation+'''}

void FFT2D5Poisson::copyOccupiedSlices(std::span<const size_t> occupied) {
'''+slices+'''}

void FFT2D5Poisson::prepareBatchGreen() {
    const bool localMPI = ippl::Comm->size() > 1;
    const size_t nr = nx2_ * ny2_, ncx = nx2_ / 2 + 1, nc = ncx * ny2_;
'''+green+'''}

void FFT2D5Poisson::prepareRowExecutors(int count) {
    const auto nx2 = nx2_, ny2 = ny2_;
    const size_t ncx = nx2 / 2 + 1;
'''+rows+'''}

void FFT2D5Poisson::packBatch(
        const ScalarField3_t& density, size_t first, int count, double coupling) {
'''+real+'''    const auto source = density.getView(), slices = batchSlices_m;
    const auto mesh = density.get_mesh();
    const size_t nx = mesh.getGridsize(0), ny = mesh.getGridsize(1);
    const auto ghost = density.getNghost();
    using Policy = Kokkos::MDRangePolicy<Kokkos::Rank<3>>;
'''+pack+'''}

void FFT2D5Poisson::transformBatch(int count, bool forward) {
'''+spectrum+'''    timedPhase(forward ? "2D5 FFT Rho" : "2D5 FFT Back", [&] {
        if (forward) {
'''+fftforward+'''        } else {
'''+fftback+'''        }
    });
}

void FFT2D5Poisson::multiplyBatchGreen(int count) {
    const auto columns = batchColumns_m, green = batchGreen_m;
    const size_t ncx = nx2_ / 2 + 1, nc = ncx * ny2_;
    const auto ny2 = ny2_;
    const auto scaling = dr_[0] * dr_[1];
'''+mult+'''}

void FFT2D5Poisson::extractBatchFields(
        VectorField3_t& electric, ScalarField3_t* potential, size_t first, int count) {
'''+real+'''    const auto field = electric.getView(), slices = batchSlices_m;
    const auto mesh = electric.get_mesh();
    const size_t nx = mesh.getGridsize(0), ny = mesh.getGridsize(1);
    const auto eg = electric.getNghost();
    const double inv2dx = 1. / (2 * dr_[0]), inv2dy = 1. / (2 * dr_[1]);
    using Policy = Kokkos::MDRangePolicy<Kokkos::Rank<3>>;
'''+field+'''}
'''
# Different view types cannot share a C++ auto declaration.
new=new.replace('const auto source = density.getView(), slices = batchSlices_m;', 'const auto source = density.getView();\n    const auto slices = batchSlices_m;').replace('const auto field = electric.getView(), slices = batchSlices_m;', 'const auto field = electric.getView();\n    const auto slices = batchSlices_m;').replace('const auto real = batchReal_m, spectrum = batchSpectrum_m;', 'const auto real = batchReal_m;\n    const auto spectrum = batchSpectrum_m;')
s=s[:start]+new;s=s.replace('  // Really?','');p.write_text(s)
p=Path('src/SpaceCharge/FFT2D5/FFT2D5Poisson.h');s=p.read_text();pos=s.index('private:');helpers='''    /** @internal @brief Validate local slice indices and refresh MPI geometry metadata.
     * @param density Source mesh and local slab. @param occupied Unique local slice indices.
     * @param batchSize Positive requested capacity. @return Capacity bounded by local planes.
     * @throws OpalException For invalid indices or an unmatched single-rank workspace. */
    int validateBatchGeometry(const ScalarField3_t& density,
                              std::span<const size_t> occupied, int batchSize);
    /** @internal @brief Resize batch buffers and invalidate cached row plans only when needed.
     * @param capacity Maximum planes per batch. MPI Green initialization receives one
     * plan workspace, independent of capacity; single-rank rows allocate none of that scratch. */
    void prepareBatchBuffers(int capacity);
    /** @internal @brief Copy the occupied local slice list to its reusable device buffer.
     * @param occupied Unique physical local indices, already validated. */
    void copyOccupiedSlices(std::span<const size_t> occupied);
    /** @internal @brief Initialize the normalized Green spectrum without transforming z.
     * MPI uses one private 2D transform; one rank copies the existing serial spectrum. */
    void prepareBatchGreen();
    /** @internal @brief Cache native x/y row executors for the actual full/remainder size.
     * @param count Positive planes in this batch; retains at most full and final-size plans. */
    void prepareRowExecutors(int count);
    /** @internal @brief Pack source cells into zero-padded batch planes, applying coupling.
     * @param density Unmodified source. @param first Offset in the occupied list.
     * @param count Planes in this batch. @param coupling Electrostatic source multiplier. */
    void packBatch(const ScalarField3_t& density, size_t first, int count, double coupling);
    /** @internal @brief Transform x rows/y columns in the original execution order.
     * @param count Actual batch size with cached executors. @param forward Select forward
     * R2C/transpose/C2C or inverse C2C/transpose/C2R; transforms remain unscaled. */
    void transformBatch(int count, bool forward);
    /** @internal @brief Multiply column spectra by Green and source-cell area.
     * @param count Number of active planes; no longitudinal mixing occurs. */
    void multiplyBatchGreen(int count);
    /** @internal @brief Extract centered transverse fields and optional potential halos.
     * @param electric Destination physical fields. @param potential Optional verification grid.
     * @param first Offset in occupied slices. @param count Number of active planes.
     * Helpers launching CUDA extended lambdas stay public for NVCC accessibility. */
    void extractBatchFields(VectorField3_t& electric, ScalarField3_t* potential,
                            size_t first, int count);

''';s=s[:pos]+helpers+s[pos:];s=s.replace('    template <class Work>\n    void timedPhase','''    /** @brief Execute a phase with completed-device timing except during zero-source warmup.
     * @tparam Work Host callable launching a complete phase. @param name Registered timer.
     * @param work Work to execute; exception-safe timing is delegated to the shared helper. */
    template <class Work>
    void timedPhase''');s=s.replace('    // Mixed primitive of log(sqrt(x*x+y*y)), extended continuously to the axes.\n    // Using atan2 on absolute coordinates preserves the odd symmetry in each\n    // coordinate without branch jumps across the source-cell singularity.','''    /** @brief Mixed primitive of log(sqrt(x*x+y*y)), continued to the coordinate axes.
     * @param x First corner coordinate. @param y Second corner coordinate.
     * @return Odd-in-each-coordinate primitive, with zero value on either axis.
     * Absolute-coordinate atan2 avoids branch jumps across the source-cell singularity. */''');p.write_text(s)
