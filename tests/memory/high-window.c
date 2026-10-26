/* No high host addresses and no data copies. Native mmap owns the backing.
 * Holes retain PROT_NONE reservations, so MAP_FIXED cannot overwrite a host
 * allocation subsequently placed into a freed interior page.
 * SPDX-License-Identifier: MIT */
#include "high-window.h"
#include <sys/mman.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
struct rm_high_region rm_high_regions[16];
void (*rm_high_changed)(uint32_t,uint32_t,int);
static int valid(uint32_t addr,uint32_t bytes)
{
 return addr>=0xc0000000U && !(addr&4095) && bytes && !(bytes&4095) &&
        (uint64_t)addr+bytes<=0x100000000ULL;
}
static struct rm_high_region *region(uint32_t a,uint32_t n)
{
 unsigned i;
 for(i=0;i<16;i++)if(rm_high_regions[i].bytes && a>=rm_high_regions[i].guest &&
   (uint64_t)a+n<=(uint64_t)rm_high_regions[i].guest+rm_high_regions[i].bytes)return rm_high_regions+i;
 return 0;
}
uintptr_t rm_high_host(uintptr_t a)
{
 struct rm_high_region *r=a<=0xffffffffU?region(a,1):0;
 return r?r->host+(a-r->guest):a;
}
uintptr_t rm_high_guest(uintptr_t a)
{
 unsigned i;
 for(i=0;i<16;i++)if(rm_high_regions[i].bytes && a>=rm_high_regions[i].host &&
  a-rm_high_regions[i].host<rm_high_regions[i].bytes)return rm_high_regions[i].guest+(a-rm_high_regions[i].host);
 return a;
}
int rm_high_backing(uintptr_t a,uint32_t n)
{
 unsigned i;
 for(i=0;i<16;i++)if(rm_high_regions[i].bytes && (uint64_t)a+n>rm_high_regions[i].host &&
  a<(uint64_t)rm_high_regions[i].host+rm_high_regions[i].bytes)return 1;
 return 0;
}
int rm_high_contains(uint32_t a,uint32_t n)
{
 struct rm_high_region *r=region(a,n);unsigned first,last,i;
 if(!r || !n)return 0;
 first=(a-r->guest)/4096;last=(a-r->guest+n-1)/4096;
 for(i=first;i<=last;i++)if(!r->mapped[i])return 0;
 return 1;
}
long rm_high_map(uint32_t a,uint32_t n,int prot,int flags,int fd,uint32_t off)
{
 struct rm_high_region *r;unsigned i;void *p;int fresh=0;
 if(!valid(a,n) || !(flags&MAP_FIXED) || (off&4095)){errno=EINVAL;return -1;}
 /* Executable high pages require additional TB/SMC verification. */
 if(prot&PROT_EXEC){errno=ENOTSUP;return -1;}
 r=region(a,n);
 if(!r) {
  for(i=0;i<16;i++)if(rm_high_regions[i].bytes && (uint64_t)a+n>rm_high_regions[i].guest &&
   a<(uint64_t)rm_high_regions[i].guest+rm_high_regions[i].bytes){errno=EINVAL;return -1;}
  for(i=0;i<16 && rm_high_regions[i].bytes;i++);
  if(i==16){errno=ENOMEM;return -1;}
  p=mmap((void *)(uintptr_t)(0x50000000U+i*0x04000000U),n,PROT_NONE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
  if(p==MAP_FAILED)return -1;
  if((uintptr_t)p<4096 || (uint64_t)(uintptr_t)p+n>0xc0000000ULL){munmap(p,n);errno=ENOMEM;return -1;}
  r=rm_high_regions+i;
  r->mapped=calloc(n/4096,1);
  if(!r->mapped){munmap(p,n);errno=ENOMEM;return -1;}
  r->guest=a;r->bytes=n;r->host=(uintptr_t)p;fresh=1;
 }
 p=mmap((void *)(r->host+(a-r->guest)),n,prot,flags,fd,off);
 if(p==MAP_FAILED) {
  if(fresh){munmap((void *)r->host,n);free(r->mapped);memset(r,0,sizeof(*r));}
  return -1;
 }
 memset(r->mapped+(a-r->guest)/4096,1,n/4096);
 if(rm_high_changed)rm_high_changed(a,n,prot);
 return (long)a;
}
int rm_high_unmap(uint32_t a,uint32_t n)
{
 struct rm_high_region *r=region(a,n);int result;
 if(!valid(a,n) || !r){errno=EINVAL;return -1;}
 if(a==r->guest && n==r->bytes) {
  result=munmap((void *)r->host,n);if(result)return result;free(r->mapped);memset(r,0,sizeof(*r));
 } else if(mmap((void *)(r->host+(a-r->guest)),n,PROT_NONE,MAP_FIXED|MAP_PRIVATE|MAP_ANONYMOUS,-1,0)==MAP_FAILED)return -1;
 if(r->bytes)memset(r->mapped+(a-r->guest)/4096,0,n/4096);
 if(rm_high_changed)rm_high_changed(a,n,-1);
 return 0;
}
int rm_high_protect(uint32_t a,uint32_t n,int prot)
{
 struct rm_high_region *r=region(a,n);
 if(!valid(a,n) || !r){errno=EINVAL;return -1;}
 if(!rm_high_contains(a,n)){errno=ENOMEM;return -1;}
 if(prot&PROT_EXEC){errno=ENOTSUP;return -1;}
 if(mprotect((void *)(r->host+(a-r->guest)),n,prot))return -1;
 if(rm_high_changed)rm_high_changed(a,n,prot);
 return 0;
}
