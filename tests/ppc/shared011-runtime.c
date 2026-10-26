/* Same caller on native i386 and translated PPC; original IOKit only.
 * SPDX-License-Identifier: MIT */
#include <mach/mach.h>
#include <stdio.h>
extern kern_return_t IOMasterPort(mach_port_t,mach_port_t *);
extern void *IOServiceMatching(const char *);
extern kern_return_t IOServiceGetMatchingServices(mach_port_t,void *,mach_port_t *);
extern mach_port_t IOIteratorNext(mach_port_t);
extern kern_return_t IOServiceOpen(mach_port_t,mach_port_t,unsigned int,mach_port_t *);
extern kern_return_t IOServiceClose(mach_port_t);
extern kern_return_t IOConnectMethodScalarIScalarO(mach_port_t,unsigned int,unsigned int,unsigned int,...);
extern kern_return_t io_connect_map_memory(mach_port_t,int,mach_port_t,vm_address_t *,vm_size_t *,int);
extern kern_return_t io_connect_unmap_memory(mach_port_t,int,mach_port_t,vm_address_t);
extern kern_return_t mach_make_memory_entry_64(mach_port_t,unsigned long long *,unsigned long long,vm_prot_t,mach_port_t *,mach_port_t);
extern kern_return_t io_connect_method_scalarI_structureI(mach_port_t,int,const unsigned *,unsigned,const char *,unsigned);
extern int IOTrySpinLock(volatile int *);
extern void IOSpinUnlock(volatile int *);
#define CHECK(x) do {if(!(x)){fprintf(stderr,"FAIL line=%d\n",__LINE__);return 1;}}while(0)
int main(void)
{
 mach_port_t master=0,iter=0,service=0,conn=0;vm_address_t address=0;vm_size_t bytes=0;
 volatile unsigned *words;volatile unsigned char *raw;unsigned saved,neighbor;
 {
  vm_address_t source=0,view=0;unsigned long long length=4096;mach_port_t entry=0;
  CHECK(!vm_allocate(mach_task_self(),&source,4096,1));
  *(volatile unsigned *)source=0x13579bdf;
  CHECK(!mach_make_memory_entry_64(mach_task_self(),&length,source,3,&entry,0));
  CHECK(entry && length==4096);
  CHECK(!vm_map(mach_task_self(),&view,4096,0,1,entry,0,0,3,3,VM_INHERIT_NONE));
  printf("anonymous entry source=%08x alias=%08x port=%u\n",*(volatile unsigned *)source,*(volatile unsigned *)view,entry);
  CHECK(*(volatile unsigned *)view==0x13579bdf);
  *(volatile unsigned *)view=0x2468ace0;CHECK(*(volatile unsigned *)source==0x2468ace0);
  CHECK(!vm_deallocate(mach_task_self(),view,4096) && !vm_deallocate(mach_task_self(),source,4096));
  CHECK(!mach_port_deallocate(mach_task_self(),entry));
  puts("anonymous Mach entry bidirectional original bytes OK");
 }
 CHECK(!IOMasterPort(0,&master));
 CHECK(!IOServiceGetMatchingServices(master,IOServiceMatching("IOFramebuffer"),&iter));
 while((service=IOIteratorNext(iter))) {
  if(!IOServiceOpen(service,mach_task_self(),0,&conn))break;
  CHECK(!mach_port_deallocate(mach_task_self(),service));
 }
 CHECK(service && conn);
 CHECK(!IOConnectMethodScalarIScalarO(conn,0,3,0,0x00100003,64,64));
 CHECK(!io_connect_map_memory(conn,100,mach_task_self(),&address,&bytes,1));
 words=(volatile unsigned *)address;raw=(volatile unsigned char *)address;
 CHECK(words[14]==3 && words[15]==bytes && bytes==278764);
 saved=words[20];neighbor=words[21];words[20]=0x12345678;
 CHECK(words[20]==0x12345678);
#ifdef __ppc__
 raw[81]=0xab;CHECK(words[20]==0x12ab5678);
 *(volatile unsigned short *)(address+82)=0xcdef;
#else
 raw[82]=0xab;CHECK(words[20]==0x12ab5678);
 *(volatile unsigned short *)(address+80)=0xcdef;
#endif
 CHECK(words[20]==0x12abcdef);
 CHECK(words[21]==neighbor);words[20]=saved;
 CHECK(IOTrySpinLock((volatile int *)address));CHECK(words[0]==1);
 CHECK(!IOTrySpinLock((volatile int *)address));IOSpinUnlock((volatile int *)address);CHECK(words[0]==0);
 printf("live framebuffer version=%u bytes=%u partial16/32 original-spinlock neighbors OK\n",words[14],(unsigned)bytes);
 {
  unsigned long long length=bytes;vm_address_t alias=0;mach_port_t entry=0;
  CHECK(!vm_inherit(mach_task_self(),address,bytes,VM_INHERIT_NONE));
  CHECK(!mach_make_memory_entry_64(mach_task_self(),&length,address,VM_PROT_READ|VM_PROT_WRITE,&entry,0));
  CHECK(!vm_map(mach_task_self(),&alias,(vm_size_t)length,0,1,entry,0,0,VM_PROT_READ|VM_PROT_WRITE,VM_PROT_READ|VM_PROT_WRITE,VM_INHERIT_NONE));
  printf("IOKit entry native alias diagnostic source=%08x alias=%08x bytes=%u length=%u addresses=%08x,%08x\n",words[14],*(volatile unsigned *)(alias+56),(unsigned)bytes,(unsigned)length,(unsigned)address,(unsigned)alias);
  /* Check identity, not just the initial zero value. The i386 IOKit
   * pmap mapping is not a named VM-object alias on this kernel. */
  {
   unsigned src=words[20],dst=*(volatile unsigned *)(alias+80);
   *(volatile unsigned *)(alias+80)=0x55aa2468;
   CHECK(words[20]==src);
   words[20]=0x66771357;
   CHECK(*(volatile unsigned *)(alias+80)==0x55aa2468);
   words[20]=src;*(volatile unsigned *)(alias+80)=dst;
   puts("IOKit named entry is physically disjoint: bidirectional isolation verified");
  }
  CHECK(!vm_deallocate(mach_task_self(),alias,(vm_size_t)length));CHECK(!mach_port_deallocate(mach_task_self(),entry));
  puts("native memory-entry diagnostic retained; physical IOKit aliases tested separately");
 }
 {
  vm_address_t second=0x30000000;vm_size_t secondbytes=0;
  CHECK(!vm_allocate(mach_task_self(),&second,(bytes+4095)&~4095,0));
  CHECK(!vm_deallocate(mach_task_self(),second,(bytes+4095)&~4095));
  CHECK(!io_connect_map_memory(conn,100,mach_task_self(),&second,&secondbytes,0));
  CHECK(second!=address && secondbytes==bytes && *(volatile unsigned *)(second+56)==3);
  saved=words[20];*(volatile unsigned *)(second+80)=0x13579bdf;CHECK(words[20]==0x13579bdf);
  words[20]=saved;CHECK(*(volatile unsigned *)(second+80)==saved);
  saved=*(volatile unsigned *)(address+236);*(volatile unsigned *)(second+236)=0xa1b2c3d4;
  CHECK(*(volatile unsigned *)(address+236)==0xa1b2c3d4);*(volatile unsigned *)(address+236)=saved;
  {
   unsigned a=*(volatile unsigned *)(address+240),b=*(volatile unsigned *)(address+244);
#ifdef __ppc__
   *(volatile double *)(second+240)=1.0;
#else
   *(volatile unsigned *)(second+240)=0x3ff00000;*(volatile unsigned *)(second+244)=0;
#endif
   CHECK(*(volatile unsigned *)(address+240)==0x3ff00000 && *(volatile unsigned *)(address+244)==0);
#ifdef __ppc__
   CHECK(*(volatile double *)(address+240)==1.0);
#endif
   *(volatile unsigned *)(address+240)=a;*(volatile unsigned *)(address+244)=b;
   puts("cursor paired32 lfd/stfd original aliases restore OK");
  }
  {
   unsigned short x=*(volatile unsigned short *)(address+220),y=*(volatile unsigned short *)(address+222);
   *(volatile unsigned short *)(address+220)=0x1234;*(volatile unsigned short *)(address+222)=0x5678;
#ifdef __ppc__
   CHECK(*(volatile unsigned *)(second+220)==0x12345678);
   *(volatile unsigned *)(second+220)=0xaabbccdd;
#else
   CHECK(*(volatile unsigned *)(second+220)==0x56781234);
   *(volatile unsigned *)(second+220)=0xccddaabb;
#endif
   CHECK(*(volatile unsigned short *)(address+220)==0xaabb && *(volatile unsigned short *)(address+222)==0xccdd);
   *(volatile unsigned short *)(address+220)=x;*(volatile unsigned short *)(address+222)=y;
   puts("original cursor packed coordinates word32 preserves two native16 fields OK");
  }
  CHECK(!vm_protect(mach_task_self(),second,secondbytes,0,VM_PROT_READ));CHECK(*(volatile unsigned *)(second+56)==3);
  CHECK(!io_connect_unmap_memory(conn,100,mach_task_self(),second));
  puts("physical IOKit aliases bidirectional cursor32 protect unmap OK");
 }
 {
  unsigned input[3]={3,256,16},j;unsigned short gamma[768];kern_return_t result;
  for(j=0;j<768;j++)gamma[j]=(j%256)*257;
  result=io_connect_method_scalarI_structureI(conn,11,input,3,(char *)gamma,sizeof(gamma));
  printf("original gamma16 identity result=%u\n",result);
 }
 {
  vm_address_t front=0,alias=0;vm_size_t frontbytes=0,aliasbytes=0;
  unsigned aperture=0,offset=0,outcount=1,save[2];volatile unsigned *p,*q;
  CHECK(!IOConnectMethodScalarIScalarO(conn,8,1,1,aperture,&offset));
  CHECK(!(offset&3));
  CHECK(!io_connect_map_memory(conn,110,mach_task_self(),&front,&frontbytes,1));
  CHECK(!vm_allocate(mach_task_self(),&alias,frontbytes,1));
  CHECK(!vm_deallocate(mach_task_self(),alias,frontbytes));
  CHECK(!io_connect_map_memory(conn,110,mach_task_self(),&alias,&aliasbytes,0));
  CHECK(front && alias!=front && frontbytes==aliasbytes && offset+8<=frontbytes);
  p=(volatile unsigned *)(front+offset);q=(volatile unsigned *)(alias+offset);
  save[0]=p[0];save[1]=p[1];
  p[0]=0x00426bad;p[1]=0x00123456;
  CHECK(q[0]==0x00426bad && q[1]==0x00123456);
  q[0]=0x00abcdef;CHECK(p[0]==0x00abcdef);
#ifdef __ppc__
  CHECK(*(volatile unsigned char *)p==0 && *((volatile unsigned char *)p+1)==0xab);
#else
  CHECK(*(volatile unsigned char *)p==0xef && *((volatile unsigned char *)p+1)==0xcd);
#endif
  p[0]=save[0];p[1]=save[1];CHECK(q[0]==save[0] && q[1]==save[1]);
  CHECK(!io_connect_unmap_memory(conn,110,mach_task_self(),alias));
  CHECK(!io_connect_unmap_memory(conn,110,mach_task_self(),front));
  puts("visible VRAM native32 physical aliases endian subfields restore OK");
 }
 CHECK(!io_connect_unmap_memory(conn,100,mach_task_self(),address));CHECK(!IOServiceClose(conn));
 CHECK(!mach_port_deallocate(mach_task_self(),service));CHECK(!mach_port_deallocate(mach_task_self(),iter));
 CHECK(!IOServiceGetMatchingServices(master,IOServiceMatching("IOHIDSystem"),&iter));service=IOIteratorNext(iter);CHECK(service);
 CHECK(!IOServiceOpen(service,mach_task_self(),0,&conn));CHECK(!IOConnectMethodScalarIScalarO(conn,0,1,0,3));
 address=0;bytes=0;CHECK(!io_connect_map_memory(conn,0,mach_task_self(),&address,&bytes,1));
 words=(volatile unsigned *)address;CHECK(words[0]==8 && words[1]==bytes && bytes==20392);
 CHECK(words[16]==3); /* EvGlobals.version at offset8+56. */
 printf("live IOHID globalsOffset=%u version=%u bytes=%u OK\n",words[0],words[16],(unsigned)bytes);
 CHECK(!io_connect_unmap_memory(conn,0,mach_task_self(),address));CHECK(!IOServiceClose(conn));
 CHECK(!mach_port_deallocate(mach_task_self(),service));CHECK(!mach_port_deallocate(mach_task_self(),iter));CHECK(!mach_port_deallocate(mach_task_self(),master));
 puts("live real IOKit objects unmap rights close OK");return 0;
}
