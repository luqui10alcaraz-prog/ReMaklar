/* i386 reference for the real kernel/user IOHID shared object.
 * Read-only observation of EvOffsets; no translated implementation claimed.
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
int main(void) {
 mach_port_t master=0,iter=0,service=0,conn=0;vm_address_t address=0;vm_size_t bytes=0;kern_return_t kr;unsigned int *offsets;unsigned char *raw;unsigned int ppc;
 if(IOMasterPort(0,&master) || IOServiceGetMatchingServices(master,IOServiceMatching("IOHIDSystem"),&iter))return 1;
 service=IOIteratorNext(iter);if(!service || IOServiceOpen(service,mach_task_self(),0,&conn))return 2;
 kr=IOConnectMethodScalarIScalarO(conn,0,1,0,3);printf("real native IOHID create shared memory result=%u\n",kr);if(kr)return 3;
 kr=io_connect_map_memory(conn,0,mach_task_self(),&address,&bytes,1);printf("real native IOHID map result=%u bytes=%u\n",kr,(unsigned int)bytes);if(kr || !address || bytes<8)return 4;
 offsets=(unsigned int *)address;raw=(unsigned char *)address;ppc=(raw[0]<<24)|(raw[1]<<16)|(raw[2]<<8)|raw[3];
 printf("real native EvOffsets globals=%u end=%u raw=%02x%02x%02x%02x PPC_unadapted=%u\n",offsets[0],offsets[1],raw[0],raw[1],raw[2],raw[3],ppc);
 if(offsets[0]!=8 || offsets[1]>bytes || offsets[1]<=8 || ppc==offsets[0])return 5;
 if(io_connect_unmap_memory(conn,0,mach_task_self(),address) || IOServiceClose(conn))return 6;
 if(mach_port_deallocate(mach_task_self(),service) || mach_port_deallocate(mach_task_self(),iter) || mach_port_deallocate(mach_task_self(),master))return 7;
 puts("real native IOHID map read endian mismatch unmap close OK");return 0;
}
