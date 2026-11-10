# Field-test output isolation

Implemented seven fixture changes under unit_tests/Fields. All tests retain their generated native C++ data and assertions/tolerances. No CMake or working-directory changes. No build/tests run by this worker; root coordinates validation after the shared helper is present.

The definite cross-target collision was TestFM2DMagnetoStatic and TestFM2DDynamic: both created/deleted /tmp/opalx_fm2d_test and wrote identical map filenames. All five fixed-directory fixtures now call TemporaryDirectory::create with a descriptive prefix. TestFM3DDynamic also uses atomic directory ownership instead of timestamp naming. TestG4BL3DGrid places its stem/files under an owned directory rather than shared data/.

All seven use ../TemporaryDirectory.h and opalx::test::TemporaryDirectory. Fieldmap caches are cleared/freed before reset deletes the owner directory. Default registration is one rank; no MPI path sharing was introduced. The helper destructor must remain rank-local and nonthrowing.

Changed: TestAstra1DDynamic.cpp, TestAstra1DMagnetoStatic.cpp, TestFM2DDynamic.cpp, TestFM2DMagnetoStatic.cpp, TestFM3DDynamic.cpp, TestG4BL2DMagnetoStatic.cpp, TestG4BL3DGrid.cpp.

LLVM21 clang-format applied and git diff --check passes. Assertion-bearing source lines match the original verbatim. Source hashes and assertion checks in fields.json. Next: root provides helper, compiles these seven targets and runs them concurrently, particularly FM2D static/dynamic. No commit/push.
