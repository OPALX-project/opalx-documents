// Read-only Kokkos Tools timing callbacks. No fences or particle mutations.
#include "impl/Kokkos_Profiling_C_Interface.h"
#include <chrono>
#include <atomic>
#include <vector>
#include <map>
#include <mutex>
#include <string>
#include <cstdio>
#include <cstdlib>
#include <algorithm>
using Clock=std::chrono::steady_clock;
struct Span {uint64_t id;std::string key;Clock::time_point start;double children=0;};
struct Stat {uint64_t count=0;double inclusive=0,exclusive=0,maximum=0;};
static std::atomic<uint64_t> next_id{1},errors{0};
static std::mutex mutex;
static std::map<std::string,Stat> stats;
static thread_local std::vector<Span> stack;
static Clock::time_point initialized;
static uint64_t begin(const std::string& kind,const char* name) {auto id=next_id++;stack.push_back({id,kind+":"+(name?name:""),Clock::now(),0});return id;}
static void end(uint64_t id) {auto stop=Clock::now();if(stack.empty()||stack.back().id!=id){++errors;return;}auto s=std::move(stack.back());stack.pop_back();double t=std::chrono::duration<double>(stop-s.start).count();if(!stack.empty())stack.back().children+=t;std::lock_guard<std::mutex> lock(mutex);auto& x=stats[s.key];++x.count;x.inclusive+=t;x.exclusive+=std::max(0.,t-s.children);x.maximum=std::max(x.maximum,t);}
static std::string quote(const std::string& s){std::string r="\"";for(char c:s){if(c=='\"')r+='\"';r+=c;}return r+'\"';}
extern "C" {
void kokkosp_init_library(const int,const uint64_t,const uint32_t,Kokkos_Profiling_KokkosPDeviceInfo*) {initialized=Clock::now();std::fprintf(stderr,"[kernel-timer] loaded, synchronous OpenMP timing, no added fences\n");}
void kokkosp_request_tool_settings(const uint32_t,Kokkos_Tools_ToolSettings* s){s->requires_global_fencing=false;}
void kokkosp_begin_parallel_for(const char* n,const uint32_t,uint64_t* id){*id=begin("for",n);}
void kokkosp_end_parallel_for(uint64_t id){end(id);}
void kokkosp_begin_parallel_reduce(const char* n,const uint32_t,uint64_t* id){*id=begin("reduce",n);}
void kokkosp_end_parallel_reduce(uint64_t id){end(id);}
void kokkosp_begin_parallel_scan(const char* n,const uint32_t,uint64_t* id){*id=begin("scan",n);}
void kokkosp_end_parallel_scan(uint64_t id){end(id);}
void kokkosp_begin_fence(const char* n,const uint32_t,uint64_t* id){*id=begin("fence",n);}
void kokkosp_end_fence(uint64_t id){end(id);}
void kokkosp_begin_deep_copy(Kokkos_Profiling_SpaceHandle,const char* dst,const void*,Kokkos_Profiling_SpaceHandle,const char* src,const void*,uint64_t){begin("copy",(std::string(dst?dst:"")+" <- "+(src?src:"")).c_str());}
void kokkosp_end_deep_copy(){if(stack.empty()){++errors;return;}end(stack.back().id);}
void kokkosp_finalize_library(){const char* path=std::getenv("OPALX_KERNEL_PROFILE");if(!path)path="kernel-timings.csv";auto* f=std::fopen(path,"w");if(!f)return;std::fprintf(f,"name,count,inclusive_s,exclusive_s,max_s\n");for(const auto& [k,v]:stats)std::fprintf(f,"%s,%llu,%.17g,%.17g,%.17g\n",quote(k).c_str(),(unsigned long long)v.count,v.inclusive,v.exclusive,v.maximum);std::fclose(f);std::fprintf(stderr,"[kernel-timer] lifetime_s=%.9f callback_errors=%llu pending=%zu output=%s\n",std::chrono::duration<double>(Clock::now()-initialized).count(),(unsigned long long)errors.load(),stack.size(),path);}
}
