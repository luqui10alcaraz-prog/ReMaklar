/* Query real framebuffer clients and serialized registry properties; no drawing.
 * SPDX-License-Identifier: MIT */
#include <mach/mach.h>
#include <stdio.h>
#include <string.h>
extern kern_return_t IOMasterPort(mach_port_t,mach_port_t *);
extern void *IOServiceMatching(const char *);
extern kern_return_t IOServiceGetMatchingServices(mach_port_t,void *,mach_port_t *);
extern mach_port_t IOIteratorNext(mach_port_t);
extern kern_return_t IOServiceOpen(mach_port_t,mach_port_t,unsigned int,mach_port_t *);
extern kern_return_t IOServiceClose(mach_port_t);
extern kern_return_t IOConnectGetService(mach_port_t,mach_port_t *);
extern kern_return_t io_registry_entry_get_property(mach_port_t,const char *,char **,unsigned int *);
extern kern_return_t IOConnectSetNotificationPort(mach_port_t,unsigned int,mach_port_t,unsigned int);
extern kern_return_t io_service_add_interest_notification(mach_port_t,const char *,mach_port_t,const unsigned int *,unsigned int,mach_port_t *);
extern kern_return_t IOConnectMethodScalarIScalarO(mach_port_t,unsigned int,unsigned int,unsigned int,...);
extern int IOObjectConformsTo(mach_port_t,const char *);
extern kern_return_t IORegistryEntryCreateIterator(mach_port_t,const char *,unsigned int,mach_port_t *);
extern kern_return_t io_connect_method_scalarI_structureO(mach_port_t,int,const unsigned int *,unsigned int,char *,unsigned int *);
extern kern_return_t io_registry_entry_get_properties(mach_port_t,char **,unsigned int *);
extern kern_return_t io_registry_entry_get_path(mach_port_t,const char *,char *);
extern kern_return_t io_connect_set_properties(mach_port_t,const char *,unsigned int,unsigned int *);
extern kern_return_t io_connect_method_structureI_structureO(mach_port_t,int,const char *,unsigned int,char *,unsigned int *);
extern kern_return_t io_connect_map_memory(mach_port_t,int,mach_port_t,vm_address_t *,vm_size_t *,int);
extern kern_return_t io_connect_unmap_memory(mach_port_t,int,mach_port_t,vm_address_t);
extern kern_return_t io_connect_method_scalarI_structureI(mach_port_t,int,const unsigned int *,unsigned int,const char *,unsigned int);
extern kern_return_t IORegistryEntryGetParentIterator(mach_port_t,const char *,mach_port_t *);
int main(void) {
 mach_port_t master=0,iter=0,service=0,conn=0,associated=0;int opened=0;kern_return_t kr;
 if(IOMasterPort(0,&master) || IOServiceGetMatchingServices(master,IOServiceMatching("IOFramebuffer"),&iter))return 1;
 while((service=IOIteratorNext(iter))) {
  kr=IOServiceOpen(service,mach_task_self(),0,&conn);printf("Framebuffer open result=%u\n",kr);
  if(!kr){char *xml=0;unsigned int bytes=0;
   opened++;
   {unsigned int select=0,table[256],i;unsigned char small[16];for(i=0;i<16;i++)small[i]=(i<<1)|(i>>3);
    kr=io_connect_method_scalarI_structureI(conn,15,&select,1,(char *)small,16);printf("Framebuffer real byte color table result=%u\n",kr);if(kr)return 33;
    kr=io_connect_method_scalarI_structureI(conn,15,&select,1,(char *)small,15);printf("Framebuffer real invalid color table result=%u\n",kr);if(!kr)return 34;
    select=2;for(i=0;i<256;i++)table[i]=(i<<16)|(i<<8)|i;
    kr=io_connect_method_scalarI_structureI(conn,15,&select,1,(char *)table,sizeof(table));printf("Framebuffer real uint32 color table result=%u\n",kr);if(kr)return 35;
   }

   {unsigned int result=0;kr=io_connect_set_properties(conn,"invalid serialized property",28,&result);printf("Framebuffer real malformed properties transport=%u result=%u\n",kr,result);if(kr || !result)return 26;}

   {mach_port_t notification=0;union {mach_msg_header_t h;char bytes[128];} msg;
    if(mach_port_allocate(mach_task_self(),MACH_PORT_RIGHT_RECEIVE,&notification))return 9;
    kr=IOConnectSetNotificationPort(conn,0,notification,0);printf("Framebuffer notification registration result=%u\n",kr);if(kr)return 10;
    memset(&msg,0,sizeof(msg));kr=mach_msg(&msg.h,MACH_RCV_MSG|MACH_RCV_TIMEOUT,0,sizeof(msg),notification,10,0);
    printf("Framebuffer real notification receive result=%u bytes=%u id=%d\n",kr,msg.h.msgh_size,msg.h.msgh_id);
    if(kr && kr!=MACH_RCV_TIMED_OUT)return 11;if(!kr && (msg.h.msgh_size!=24 || msg.h.msgh_id>1))return 12;
    if(IOConnectSetNotificationPort(conn,0,MACH_PORT_NULL,0) || mach_port_destroy(mach_task_self(),notification))return 13;
   }
   kr=IOConnectGetService(conn,&associated);if(kr || !associated)return 2;
   if(!IOObjectConformsTo(associated,"IONDRVFramebuffer") || IOObjectConformsTo(associated,"Remaklar010Missing"))return 18;puts("Framebuffer real metaclass conforms positive negative OK");
   {mach_port_t parents=0,node=0;unsigned int count=0;kr=IORegistryEntryGetParentIterator(associated,"IOService",&parents);if(kr || !parents)return 36;
    while((node=IOIteratorNext(parents))){count++;if(mach_port_deallocate(mach_task_self(),node))return 37;}
    if(!count || mach_port_deallocate(mach_task_self(),parents))return 38;printf("Framebuffer real registry parents=%u\n",count);
   }
   {char path[512]={0};kr=io_registry_entry_get_path(associated,"IOService",path);if(kr || !strstr(path,"IOService:"))return 25;printf("Framebuffer real registry path: %s\n",path);}
   {mach_port_t children=0,node=0;unsigned int nodes=0,displays=0;
    kr=IORegistryEntryCreateIterator(associated,"IOService",1,&children);if(kr || !children)return 19;
    while((node=IOIteratorNext(children))){nodes++;if(IOObjectConformsTo(node,"IODisplay"))displays++;if(mach_port_deallocate(mach_task_self(),node))return 20;}
    if(mach_port_deallocate(mach_task_self(),children))return 21;printf("Framebuffer real registry traversal nodes=%u displays=%u\n",nodes,displays);
   }
   {unsigned int mode=0,depth=0;
   {unsigned int count=0,modes[128],bytes;kr=IOConnectMethodScalarIScalarO(conn,6,0,1,&count);if(kr || !count || count>128)return 27;bytes=count*4;
    kr=io_connect_method_structureI_structureO(conn,7,0,0,(char *)modes,&bytes);printf("Framebuffer real modes result=%u count=%u bytes=%u first=%u\n",kr,count,bytes,modes[0]);if(kr || bytes!=count*4)return 28;
   }
kr=IOConnectMethodScalarIScalarO(conn,2,0,2,&mode,&depth);printf("Framebuffer real current mode result=%u mode=%u depth=%u\n",kr,mode,depth);if(kr)return 14;{
    unsigned int input=mode,description[51]={0},bytes=sizeof(description);
    kr=io_connect_method_scalarI_structureO(conn,5,&input,1,(char *)description,&bytes);
    printf("Framebuffer real mode description result=%u bytes=%u width=%u height=%u flags=%x timing=%x\n",kr,bytes,description[0],description[1],description[4],description[10]);if(kr || bytes!=204 || !description[0] || !description[1])return 29;
    input=0xffffffff;bytes=sizeof(description);kr=io_connect_method_scalarI_structureO(conn,5,&input,1,(char *)description,&bytes);printf("Framebuffer real invalid mode result=%u\n",kr);if(!kr)return 30;
   }{
    unsigned int input[3],pixels[43],bytes=sizeof(pixels);input[0]=mode;input[1]=depth;input[2]=0;memset(pixels,0,sizeof(pixels));
    kr=io_connect_method_scalarI_structureO(conn,1,input,3,(char *)pixels,&bytes);
    printf("Framebuffer real pixel info result=%u bytes=%u width=%u height=%u bpp=%u row=%u format=%s\n",kr,bytes,pixels[39],pixels[40],pixels[2],pixels[0],(char *)pixels+88);
    if(kr || bytes!=172 || !pixels[39] || !pixels[40])return 22;
   }}
   {mach_port_t wake=0,notification=0;unsigned int refs[8]={0,0x11223344,0x55667788,0};refs[3]=associated;
    if(mach_port_allocate(mach_task_self(),MACH_PORT_RIGHT_RECEIVE,&wake))return 15;
    kr=io_service_add_interest_notification(associated,"IOGeneralInterest",wake,refs,4,&notification);printf("Framebuffer interest registration result=%u nonnull=%d\n",kr,notification!=0);if(kr || !notification)return 16;
    if(mach_port_deallocate(mach_task_self(),notification) || mach_port_destroy(mach_task_self(),wake))return 17;
   }
   kr=io_registry_entry_get_property(associated,"IOClass",&xml,&bytes);printf("Framebuffer IOClass result=%u bytes=%u\n",kr,bytes);if(kr || !xml || !bytes)return 3;printf("Framebuffer class XML: %s\n",xml);
   if(vm_deallocate(mach_task_self(),(vm_address_t)xml,bytes))return 4;
   xml=0;bytes=0;kr=io_registry_entry_get_properties(associated,&xml,&bytes);if(kr || !xml || !bytes || !strstr(xml,"<dict") || !strstr(xml,"IONDRVFramebuffer"))return 23;
   puts("Framebuffer real serialized property dictionary OK");if(vm_deallocate(mach_task_self(),(vm_address_t)xml,bytes))return 24;
   xml=0;bytes=0;kr=io_registry_entry_get_property(associated,"Remaklar010Missing",&xml,&bytes);printf("Framebuffer missing property result=%u\n",kr);if(!kr)return 5;
   {vm_address_t address=0;vm_size_t bytes=0;kr=io_connect_map_memory(conn,110,mach_task_self(),&address,&bytes,1);printf("Framebuffer real VRAM map result=%u bytes=%u\n",kr,(unsigned int)bytes);
    if(!kr){volatile unsigned char byte;if(!address || !bytes)return 31;byte=*(volatile unsigned char *)address;(void)byte;if(io_connect_unmap_memory(conn,110,mach_task_self(),address))return 32;puts("Framebuffer real VRAM read unmap OK");}
   }
   if(mach_port_deallocate(mach_task_self(),associated) || IOServiceClose(conn))return 6;
  }
  if(mach_port_deallocate(mach_task_self(),service))return 7;
 }
 if(mach_port_deallocate(mach_task_self(),iter) || mach_port_deallocate(mach_task_self(),master) || !opened)return 8;
 puts("real framebuffer open associated service property errors close OK");return 0;
}
