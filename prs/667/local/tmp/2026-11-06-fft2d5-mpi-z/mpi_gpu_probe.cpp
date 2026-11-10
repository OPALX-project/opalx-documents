#include <mpi.h>
#include <cuda_runtime_api.h>
#include <cstdio>
#include <cstdlib>
#include <vector>
int main(int argc,char**argv){
 MPI_Init(&argc,&argv);int rank=0,size=0,count=0;MPI_Comm_rank(MPI_COMM_WORLD,&rank);MPI_Comm_size(MPI_COMM_WORLD,&size);
 int expected=(argc>1?std::atoi(argv[1]):0);cudaDeviceProp prop{};
 bool ok=size==expected&&cudaGetDeviceCount(&count)==cudaSuccess&&count==1&&cudaGetDeviceProperties(&prop,0)==cudaSuccess;
 int local=ok?1:0,global=0;MPI_Allreduce(&local,&global,1,MPI_INT,MPI_MIN,MPI_COMM_WORLD);
 if(!global){std::fprintf(stderr,"BAD MPI/GPU launch rank=%d size=%d expected=%d devices=%d\n",rank,size,expected,count);MPI_Abort(MPI_COMM_WORLD,2);}
 std::vector<char> ids(size*16);MPI_Allgather(prop.uuid.bytes,16,MPI_CHAR,ids.data(),16,MPI_CHAR,MPI_COMM_WORLD);
 for(int a=0;a<size;++a)for(int b=0;b<a;++b){bool equal=true;for(int d=0;d<16;++d)equal&=ids[a*16+d]==ids[b*16+d];if(equal)MPI_Abort(MPI_COMM_WORLD,3);}
 std::printf("VERIFIED rank=%d world=%d visible_devices=%d GPU=%s UUID=",rank,size,count,prop.name);
 for(int d=0;d<16;++d)std::printf("%02x",static_cast<unsigned char>(prop.uuid.bytes[d]));std::printf("\n");
 MPI_Finalize();return 0;
}
