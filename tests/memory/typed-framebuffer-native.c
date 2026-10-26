/* Native isolated live view of the real IOGraphics-40 shared object.
 * SPDX-License-Identifier: MIT */
#include <mach/mach.h>
#include <stdio.h>
#include "typed-live.h"
extern kern_return_t io_connect_method_structureI_structureO(mach_port_t,int,const char *,unsigned int,char *,unsigned int *);
extern kern_return_t IOMasterPort(mach_port_t,mach_port_t *);
extern void *IOServiceMatching(const char *);
extern kern_return_t IOServiceGetMatchingServices(mach_port_t,void *,mach_port_t *);
extern mach_port_t IOIteratorNext(mach_port_t);
extern kern_return_t IOServiceOpen(mach_port_t,mach_port_t,unsigned int,mach_port_t *);
extern kern_return_t IOServiceClose(mach_port_t);
extern kern_return_t IOConnectMethodScalarIScalarO(mach_port_t,unsigned int,unsigned int,unsigned int,...);
extern kern_return_t io_connect_map_memory(mach_port_t,int,mach_port_t,vm_address_t *,vm_size_t *,int);
extern kern_return_t io_connect_unmap_memory(mach_port_t,int,mach_port_t,vm_address_t);
int main(void) {
 mach_port_t master=0,iter=0,service=0,conn=0;int opened=0;
 if(IOMasterPort(0,&master) || IOServiceGetMatchingServices(master,IOServiceMatching("IOFramebuffer"),&iter))return 1;
 while((service=IOIteratorNext(iter))) {
  if(!IOServiceOpen(service,mach_task_self(),0,&conn)) {
   vm_address_t address=0;vm_size_t bytes=0;kern_return_t kr;unsigned int *words;unsigned char *raw;unsigned int ppc;
   opened++;
   kr=IOConnectMethodScalarIScalarO(conn,0,3,0,0x00100003,64,64);printf("real native cursor create result=%u\n",kr);if(kr)return 2;
   kr=io_connect_map_memory(conn,100,mach_task_self(),&address,&bytes,1);printf("real native cursor map result=%u bytes=%u\n",kr,(unsigned int)bytes);if(kr || !address || bytes<80)return 3;
   /* IOGraphics-40 StdFBShmem_t: int version/structSize at offsets 56/60. */
   words=(unsigned int *)address;raw=(unsigned char *)address+56;ppc=(raw[0]<<24)|(raw[1]<<16)|(raw[2]<<8)|raw[3];
   printf("real native StdFBShmem version=%u size=%u raw=%02x%02x%02x%02x PPC_unadapted=%u\n",words[14],words[15],raw[0],raw[1],raw[2],raw[3],ppc);
   if(words[14]!=3 || words[15]>bytes || words[15]<80 || ppc==words[14])return 4;
   {
    static const struct rm_field fields[]={{48,2,0},{50,2,0},{52,2,0},{54,2,0},{56,4,0},{60,4,0},{80,4,0}};
    struct rm_view v;rm_u64 x;unsigned int saved=words[20],outsize=0;short bounds[4]={0,0,1024,768},original[4];int j;
    v.base=(unsigned char *)address;v.bytes=bytes;v.fields=fields;v.count=7;v.writable=1;
    if(rm_read(&v,56,4,&x) || x!=3)return 8;
    if(rm_write(&v,80,4,0x12345678) || words[20]!=0x12345678)return 9;
    words[20]=0xaabbccdd;
    if(rm_read(&v,80,4,&x) || x!=0xaabbccdd)return 10;
    if(rm_write(&v,81,1,0xee) || words[20]!=0xaaeeccdd)return 11;
    words[20]=saved;
    for(j=0;j<4;j++)original[j]=((short *)(address+48))[j];
    kr=io_connect_method_structureI_structureO(conn,9,(char *)bounds,8,0,&outsize);
    printf("real kernel setBounds result=%u\n",kr);if(kr)return 12;
    for(j=0;j<4;j++)if(rm_read(&v,48+2*j,2,&x) || x!=(unsigned short)bounds[j])return 13;
    if(io_connect_method_structureI_structureO(conn,9,(char *)original,8,0,&outsize))return 14;
    puts("live native framebuffer version3 bidirectional partial kernel-bounds neighbor-restore OK");
   }

   if(io_connect_unmap_memory(conn,100,mach_task_self(),address) || IOServiceClose(conn))return 5;
  }
  if(mach_port_deallocate(mach_task_self(),service))return 6;
 }
 if(!opened || mach_port_deallocate(mach_task_self(),iter) || mach_port_deallocate(mach_task_self(),master))return 7;
 puts("real native cursor map read endian mismatch unmap close OK");return 0;
}
