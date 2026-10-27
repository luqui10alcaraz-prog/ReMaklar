/* Native kernel matching dictionaries and real registry lookups.
 * No replacement XML or registry objects. SPDX-License-Identifier: MIT */
#include <mach/mach.h>
#include <stdio.h>
#include <string.h>
extern kern_return_t IOMasterPort(mach_port_t,mach_port_t *);
extern kern_return_t io_make_matching(mach_port_t,unsigned,unsigned,const char *,unsigned,char *);
extern void *IOBSDNameMatching(mach_port_t,unsigned,const char *);
extern kern_return_t IOServiceGetMatchingServices(mach_port_t,void *,mach_port_t *);
extern mach_port_t IOIteratorNext(mach_port_t);
extern kern_return_t IOObjectRelease(mach_port_t);
extern kern_return_t IORegistryEntryGetPath(mach_port_t,const char *,char *);
int main(void) {
 mach_port_t master=0,it=0,service=0;char text[512],path[512];unsigned i;kern_return_t kr;
 const char *names[]={"disk0s2","disk1s1","disk3s0","remaklar-no-such-disk"};
 if(IOMasterPort(0,&master))return 1;
 for(i=0;i<4;i++) {
  memset(text,0xcc,sizeof(text));
  kr=io_make_matching(master,101,0,names[i],strlen(names[i])+1,text);
  if(kr || !memchr(text,0,sizeof(text)) || !strstr(text,names[i]))return 2;
  printf("actual kernel BSD matching %s: %s\n",names[i],text);
  if(IOServiceGetMatchingServices(master,IOBSDNameMatching(master,0,names[i]),&it))return 3;
  service=IOIteratorNext(it);
  if(i<3) {
   if(!service || IORegistryEntryGetPath(service,"IOService",path))return 4;
   printf("actual registry path %s: %s\n",names[i],path);
  } else if(service)return 5;
  if(service)IOObjectRelease(service);IOObjectRelease(it);
 }
 memset(text,0xcc,sizeof(text));kr=io_make_matching(master,100,0,"",0,text);
 printf("actual kernel general matching result=%u text=%s\n",kr,kr?"<error>":text);if(kr)return 6;
 kr=io_make_matching(master,0x76543210,0,"",0,text);
 printf("actual kernel unknown matching type result=%u\n",kr);if(!kr)return 7;
 IOObjectRelease(master);puts("real kernel dictionary serialization and device enumeration OK");return 0;
}
