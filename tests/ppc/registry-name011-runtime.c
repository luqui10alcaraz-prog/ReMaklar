/* Compare original kernel names in actual registry planes. SPDX-License-Identifier: MIT */
#include <mach/mach.h>
#include <stdio.h>
#include <string.h>
extern kern_return_t IOMasterPort(mach_port_t,mach_port_t *);
extern void *IOBSDNameMatching(mach_port_t,unsigned,const char *);
extern kern_return_t IOServiceGetMatchingServices(mach_port_t,void *,mach_port_t *);
extern mach_port_t IOIteratorNext(mach_port_t);
extern kern_return_t IOObjectRelease(mach_port_t);
extern kern_return_t IORegistryEntryGetNameInPlane(mach_port_t,const char *,char *);
int main(int argc,char **argv) {
 const char *devices[]={"disk0s2","disk1s1","disk3s0"};
 const char *planes[]={"IOService","","ReMaklar-No-Such-Plane"};
 mach_port_t master=0,it=0,obj=0;unsigned i,j;char name[128];kern_return_t kr;
 if(argc>1)devices[1]=argv[1];
 if(IOMasterPort(0,&master))return 1;
 for(i=0;i<3;i++){
  if(IOServiceGetMatchingServices(master,IOBSDNameMatching(master,0,devices[i]),&it))return 2;
  obj=IOIteratorNext(it);if(!obj)return 3;
  for(j=0;j<3;j++){
   memset(name,0xcc,sizeof(name));kr=IORegistryEntryGetNameInPlane(obj,planes[j],name);
   if(!kr && (!memchr(name,0,sizeof(name)) || !name[0]))return 4;
   printf("real registry %s plane=%s result=%u name=%s\n",devices[i],planes[j],kr,kr?"<error>":name);
  }
  IOObjectRelease(obj);IOObjectRelease(it);
 }
 IOObjectRelease(master);puts("native kernel registry names, empty and unknown planes observed OK");return 0;
}
