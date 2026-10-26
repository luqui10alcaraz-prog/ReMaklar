/* Bounded guest-high / host-low windows. SPDX-License-Identifier: MIT */
#ifndef RM_HIGH_WINDOW_H
#define RM_HIGH_WINDOW_H
#include <sys/types.h>
#include <stdint.h>
#include <sys/mman.h>
#ifndef MAP_ANONYMOUS
#define MAP_ANONYMOUS MAP_ANON
#endif
struct rm_high_region { uint32_t guest,bytes;uintptr_t host;unsigned char *mapped; };
extern struct rm_high_region rm_high_regions[16];
extern void (*rm_high_changed)(uint32_t,uint32_t,int);
uintptr_t rm_high_host(uintptr_t);
uintptr_t rm_high_guest(uintptr_t);
int rm_high_backing(uintptr_t,uint32_t);
int rm_high_contains(uint32_t,uint32_t);
long rm_high_map(uint32_t,uint32_t,int,int,int,uint32_t);
int rm_high_unmap(uint32_t,uint32_t);
int rm_high_protect(uint32_t,uint32_t,int);
#endif
