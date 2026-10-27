/* Observe and consume only events from the real IOHID kernel object.
 * Test inputs come through QEMU's actual emulated input hardware.
 * SPDX-License-Identifier: MIT */
#include <mach/mach.h>
#include <stddef.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
/* Exact v3 wire fields from IOHIDFamily-33. Avoid the incomplete Carbon SDK
 * dependencies of the installed Darwin-only IOKitLib.h. No object is faked. */
typedef mach_port_t io_iterator_t,io_object_t,io_service_t,io_connect_t;
typedef union {
 unsigned char opaque[48];
 struct {unsigned short origCharSet;short repeat;unsigned short charSet,charCode,keyCode,origCharCode;int reserved1;unsigned keyboardType;int reserved2,reserved3,reserved4,reserved5[4];} key;
 struct {unsigned char subx,suby;short eventNum;int click;unsigned char pressure,reserved1,subType,reserved2;int reserved3;unsigned char inactive[32];} mouse;
 struct {int dx,dy;unsigned char subx,suby,subType,reserved1;int reserved2;unsigned char inactive[32];} mouseMove;
 struct {short reserved,subType;int L[11];} compound;
 struct {short reserved,eventNum;int trackingNum,userData,reserved1[9];} tracking;
} NXEventData;
typedef struct {int type;struct {int x,y;} location;unsigned long long time;int flags;unsigned window;NXEventData data;} NXEvent;
typedef struct {int next,sema;NXEvent event;} NXEQElement;
typedef volatile struct {int evGlobalsOffset,evShmemOffset;} EvOffsets;
typedef volatile struct {
 int cursorSema,LLEHead,LLETail,LLELast,eNum,buttons,eventFlags,VertRetraceClock;
 struct {short x,y;} cursorLoc;int frame;short workBounds[4],mouseRect[4];
 int version,structSize,lastFrame;unsigned reservedA[31],bits;
 int movedMask,AALastEventSent,AALastEventConsumed,waitCursorSema,waitCursorUp;
 char ctxtTimedOut,waitCursorEnabled,globalWaitCursorEnabled,pad;int waitThreshold;
 NXEQElement lleq[240];
} EvGlobals;
#define NX_LMOUSEDOWN 1
#define NX_RMOUSEDRAGGED 7
#define NX_KEYDOWN 10
#define NX_KEYUP 11
#define NX_FLAGSCHANGED 12
#define LLEQSIZE 240
#define kIOMasterPortDefault 0
extern void *IOServiceMatching(const char *);
extern kern_return_t IOServiceGetMatchingServices(mach_port_t,void *,mach_port_t *);
extern mach_port_t IOIteratorNext(mach_port_t);
extern kern_return_t IOObjectRelease(mach_port_t);
extern kern_return_t IOServiceOpen(mach_port_t,mach_port_t,unsigned int,mach_port_t *);
extern kern_return_t IOServiceClose(mach_port_t);
extern kern_return_t IOConnectMethodScalarIScalarO(mach_port_t,unsigned int,unsigned int,unsigned int,...);
extern kern_return_t io_connect_map_memory(mach_port_t,int,mach_port_t,vm_address_t *,vm_size_t *,int);
extern kern_return_t io_connect_unmap_memory(mach_port_t,int,mach_port_t,vm_address_t);
extern kern_return_t io_connect_add_client(mach_port_t,mach_port_t);
static int services(const char *name) {
 io_iterator_t it=0;io_object_t obj;int count=0;
 if(IOServiceGetMatchingServices(kIOMasterPortDefault,IOServiceMatching(name),&it))return -1;
 while((obj=IOIteratorNext(it))){count++;IOObjectRelease(obj);}IOObjectRelease(it);return count;
}
static int take(volatile int *p) {
 int value=1;
#if defined(__i386__)
 __asm__ volatile("xchgl %0,%1":"=r"(value),"=m"(*p):"0"(value),"m"(*p):"memory");
#else
 __asm__ volatile("1: lwarx %0,0,%1; cmpwi %0,0; bne 2f; stwcx. %2,0,%1; bne- 1b; isync; 2:"
  :"=&r"(value):"r"(p),"r"(1):"memory","cr0");
#endif
 return value==0;
}
int main(int argc,char **argv) {
 io_iterator_t it=0;io_service_t service;io_connect_t conn=0;
 vm_address_t address=0;vm_size_t bytes=0;kern_return_t kr;EvGlobals *g;
 int i,keys=0,mice=0,letter_a=0,moves=0,downs=0,ups=0,aux=0,exits=0,reused=0,changed=0,mouse_mode=argc>1,tracking_mode=argc>2,reused_mode=argc>3,initial_x,initial_y;unsigned prior;
 mach_port_t fbit=0,fbservice=0,fbconn=0;
 setbuf(stdout,0);
 printf("layout NXEvent=%u NXEQElement=%u NXEventData=%u lleq=%u data=%u time=%u key=%u repeat=%u keyboardType=%u\n",
  sizeof(NXEvent),sizeof(NXEQElement),sizeof(NXEventData),(unsigned)offsetof(EvGlobals,lleq),
  (unsigned)offsetof(NXEQElement,event.data),(unsigned)offsetof(NXEQElement,event.time),
  (unsigned)offsetof(NXEventData,key.keyCode),(unsigned)offsetof(NXEventData,key.repeat),(unsigned)offsetof(NXEventData,key.keyboardType));
 printf("devices pointing=%d keyboard=%d ps2mouse=%d usbmouse=%d\n",services("IOHIPointing"),services("IOHIKeyboard"),services("ApplePS2Mouse"),services("IOUSBHIDDriver"));
 kr=IOServiceGetMatchingServices(kIOMasterPortDefault,IOServiceMatching("IOHIDSystem"),&it);if(kr)return 1;
 service=IOIteratorNext(it);if(!service)return 2;
 kr=IOServiceOpen(service,mach_task_self(),0,&conn);printf("open=%u\n",kr);if(kr)return 3;
 kr=IOConnectMethodScalarIScalarO(conn,0,1,0,3);printf("create=%u\n",kr);if(kr)return 4;
 kr=io_connect_map_memory(conn,0,mach_task_self(),&address,&bytes,1);printf("map=%u bytes=%u\n",kr,(unsigned)bytes);if(kr)return 5;
 g=(EvGlobals *)(address+((EvOffsets *)address)->evGlobalsOffset);
 printf("shared version=%d size=%d offsets=%d,%d\n",g->version,g->structSize,((EvOffsets *)address)->evGlobalsOffset,((EvOffsets *)address)->evShmemOffset);
 if(g->version!=3 || sizeof(NXEQElement)!=84 || offsetof(EvGlobals,lleq)!=224 || g->structSize!=sizeof(EvGlobals))return 9;
 if(argc>1 && !strcmp(argv[1],"--null-only")) {
  unsigned k,sum=0;volatile unsigned *words=(volatile unsigned *)&g->lleq[1].event.data;
  if(g->lleq[1].event.type!=0)return 16;
  for(k=0;k<12;k++)sum|=words[k];
  printf("real kernel initialized HID slot=1 type=0 data_words=12 zero=%d\n",sum==0);
  io_connect_unmap_memory(conn,0,mach_task_self(),address);IOServiceClose(conn);
  IOObjectRelease(service);IOObjectRelease(it);return sum?17:0;
 }
 kr=IOConnectMethodScalarIScalarO(conn,1,1,0,1);printf("enable=%u\n",kr);if(kr)return 6;
 if(mouse_mode) {
  kr=IOServiceGetMatchingServices(0,IOServiceMatching("IOFramebuffer"),&fbit);if(kr)return 10;
  while((fbservice=IOIteratorNext(fbit))) {
   kr=IOServiceOpen(fbservice,mach_task_self(),0,&fbconn);printf("framebuffer open=%u\n",kr);
   if(!kr)break;
   IOObjectRelease(fbservice);fbservice=0;
  }
  if(!fbservice || !fbconn)return 12;
  kr=IOConnectMethodScalarIScalarO(fbconn,0,3,0,0x00100003,64,64);printf("native cursor shared object=%u\n",kr);if(kr)return 13;
  kr=io_connect_add_client(conn,fbconn);printf("native register framebuffer=%u\n",kr);if(kr)return 14;
  g->movedMask=(1<<5)|(1<<6)|(1<<7);
  kr=IOConnectMethodScalarIScalarO(conn,2,1,0,1);printf("native enable cursor=%u\n",kr);if(kr)return 15;
 }
 initial_x=g->cursorLoc.x;initial_y=g->cursorLoc.y;
 if(tracking_mode) {
  g->mouseRect[0]=initial_x;g->mouseRect[1]=initial_x+2;
  g->mouseRect[2]=initial_y;g->mouseRect[3]=initial_y+2;
#if defined(__i386__)
  g->bits|=0x80000000U;
#else
  g->bits|=1U;
#endif
  puts("native mouseRect tracking enabled around current pointer");
 }
 puts("READY real hardware input, 15 seconds");
 prior=g->LLETail;
 for(i=0;i<150;i++) {
  unsigned head=g->LLEHead;volatile NXEQElement *e;
  if(head!=g->LLETail) {
   if(head>=LLEQSIZE)return 7;e=(NXEQElement *)&g->lleq[head];
   if(take((volatile int *)&e->sema)){
    int type=e->event.type;
    printf("event type=%d location=%d,%d",type,e->event.location.x,e->event.location.y);
    if(type==NX_KEYDOWN || type==NX_KEYUP || type==NX_FLAGSCHANGED){
     printf(" key=%u char=%u orig=%u repeat=%d keyboardType=%u",e->event.data.key.keyCode,e->event.data.key.charCode,e->event.data.key.origCharCode,e->event.data.key.repeat,e->event.data.key.keyboardType);keys++;
     if((type==NX_KEYDOWN || type==NX_KEYUP) && e->event.data.key.charCode==97 && e->event.data.key.keyCode==0)letter_a++;
    }
    if(type>=NX_LMOUSEDOWN && type<=NX_RMOUSEDRAGGED)mice++;
    if(type>=5 && type<=7){printf(" dx=%d dy=%d subtype=%u",e->event.data.mouseMove.dx,e->event.data.mouseMove.dy,e->event.data.mouseMove.subType);moves++;}
    if(type>=1 && type<=4){printf(" subxy=%u,%u eventNum=%d click=%d pressure=%u subtype=%u",e->event.data.mouse.subx,e->event.data.mouse.suby,e->event.data.mouse.eventNum,e->event.data.mouse.click,e->event.data.mouse.pressure,e->event.data.mouse.subType);if(type==1)downs++;if(type==2)ups++;}
    if(type==14 && e->event.data.compound.subType==7){printf(" auxiliary delta=%u buttons=%u",(unsigned)e->event.data.compound.L[0],(unsigned)e->event.data.compound.L[1]);aux++;}
    if(type==8 || type==9){printf(" tracking eventNum=%d number=%d userData=%d",e->event.data.tracking.eventNum,e->event.data.tracking.trackingNum,e->event.data.tracking.userData);if(type==9)exits++;}
    if(reused_mode && (type==NX_KEYDOWN || type==NX_KEYUP)) {
     unsigned k,nonzero=0;
     /* Already consumed under the real slot semaphore. Mark it inactive,
      * preserving all bytes that came from the actual hardware key event. */
     e->event.type=0;printf(" consumed-null bytes=");
     for(k=0;k<48;k++){unsigned byte=e->event.data.opaque[k];nonzero|=byte;printf("%02x",byte);}
     if(!nonzero)return 18;reused++;
    }
    puts("");g->LLEHead=e->next;
    *(volatile int *)&e->sema=0;
   }
  }
  if(g->cursorLoc.x!=initial_x || g->cursorLoc.y!=initial_y)changed=1;
  if(i%10==0)printf("tick=%d head=%d tail=%d cursor=%d,%d\n",i/10,g->LLEHead,g->LLETail,g->cursorLoc.x,g->cursorLoc.y);
  usleep(100000);
 }
 printf("DONE keys=%d letter_a=%d mice=%d initial_tail=%u final_tail=%d\n",keys,letter_a,mice,prior,g->LLETail);
 if(mouse_mode)printf("real pointer movement initial=%d,%d final=%d,%d changed=%d moves=%d downs=%d ups=%d auxiliary=%d\n",initial_x,initial_y,g->cursorLoc.x,g->cursorLoc.y,changed,moves,downs,ups,aux);
 if(tracking_mode)printf("real tracking exits=%d flags=%08x\n",exits,g->bits);
 if(reused_mode)printf("real consumed key null payloads=%d\n",reused);
 if(mouse_mode)IOConnectMethodScalarIScalarO(conn,2,1,0,0);
 IOConnectMethodScalarIScalarO(conn,1,1,0,0);
 io_connect_unmap_memory(conn,0,mach_task_self(),address);IOServiceClose(conn);
 IOObjectRelease(service);IOObjectRelease(it);
 if(fbconn)IOServiceClose(fbconn);if(fbservice)IOObjectRelease(fbservice);if(fbit)IOObjectRelease(fbit);
 return letter_a==2 && (!mouse_mode || (moves && downs && ups && aux>=2 && changed)) && (!tracking_mode || exits>0) && (!reused_mode || reused==2)?0:8;
}
