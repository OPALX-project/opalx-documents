#include "Algorithms/CyclotronProbeRecorder.h"
static_assert(sizeof(passive_probe::Endpoint)==56);
static_assert(sizeof(passive_probe::State)==72);
static_assert(sizeof(cyclotron_probe::State)==160);
static_assert(sizeof(cyclotron_probe::detail::Hit)==96);
