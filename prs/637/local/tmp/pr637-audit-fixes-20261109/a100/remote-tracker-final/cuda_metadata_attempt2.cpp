// Validation launcher metadata only; not part of OPALX or its native unit tests.
#include <cuda_runtime_api.h>
#include <iomanip>
#include <iostream>

bool checked(cudaError_t error, const char* operation) {
    if (error == cudaSuccess) return true;
    std::cerr << operation << ": " << cudaGetErrorString(error) << '\n';
    return false;
}
int main() {
    int count = 0, version = 0;
    if (!checked(cudaGetDeviceCount(&count), "cudaGetDeviceCount")) return 1;
    if (count != 1) {
        std::cerr << "Expected one visible CUDA device, saw " << count << '\n';
        return 2;
    }
    cudaDeviceProp properties{};
    if (!checked(cudaGetDeviceProperties(&properties, 0), "cudaGetDeviceProperties")
        || !checked(cudaRuntimeGetVersion(&version), "cudaRuntimeGetVersion")) return 1;
    static_assert(sizeof(properties.uuid.bytes) == 16);
    std::cout << "{\"runtime_device_count\":" << count
              << ",\"cuda_runtime_version\":" << version
              << ",\"compiled_cudart_version\":" << CUDART_VERSION
              << ",\"gpu_uuid\":\"GPU-";
    for (int i = 0; i < 16; ++i) {
        if (i == 4 || i == 6 || i == 8 || i == 10) std::cout << '-';
        std::cout << std::hex << std::setw(2) << std::setfill('0')
                  << static_cast<unsigned>(static_cast<unsigned char>(properties.uuid.bytes[i]));
    }
    std::cout << "\"}\n";
}
