/* Set actual user acceleration preferences through original IOHIDSystem.
 * No device reports, shared queue writes or kernel patches. SPDX-License-Identifier: MIT */
#include <mach/mach.h>
#include <stdio.h>
/* Public CF ABI declarations: this Darwin CD's headers omit Carbon SDK files. */
typedef const void *CFTypeRef;
typedef void *CFMutableDictionaryRef;
typedef const void *CFDataRef, *CFStringRef;
extern const char kCFTypeDictionaryKeyCallBacks[],kCFTypeDictionaryValueCallBacks[];
extern CFMutableDictionaryRef CFDictionaryCreateMutable(void *,long,const void *,const void *);
extern CFDataRef CFDataCreate(void *,const unsigned char *,long);
extern CFStringRef CFStringCreateWithCString(void *,const char *,unsigned);
extern void CFDictionarySetValue(CFMutableDictionaryRef,const void *,const void *);
extern void CFRelease(CFTypeRef);
extern void *IOServiceMatching(const char *);
extern kern_return_t IOServiceGetMatchingServices(mach_port_t,void *,mach_port_t *);
extern mach_port_t IOIteratorNext(mach_port_t);
extern kern_return_t IOObjectRelease(mach_port_t);
extern kern_return_t IORegistryEntrySetCFProperties(mach_port_t,CFTypeRef);
int main(void) {
 mach_port_t it=0,service;int value=-65536;kern_return_t kr;
 CFMutableDictionaryRef dict;CFDataRef data;CFStringRef key;int i;
 const char *keys[]={"HIDPointerAcceleration","HIDMouseAcceleration","HIDScrollAcceleration"};
 kr=IOServiceGetMatchingServices(0,IOServiceMatching("IOHIDSystem"),&it);if(kr)return 1;
 service=IOIteratorNext(it);if(!service)return 2;
 dict=CFDictionaryCreateMutable(0,0,&kCFTypeDictionaryKeyCallBacks,&kCFTypeDictionaryValueCallBacks);
 data=CFDataCreate(0,(const unsigned char *)&value,sizeof(value));
 for(i=0;i<3;i++){
  key=CFStringCreateWithCString(0,keys[i],0x0600);
  CFDictionarySetValue(dict,key,data);CFRelease(key);
 }
 kr=IORegistryEntrySetCFProperties(service,dict);
 printf("native IOHIDSystem user preferences: pointer/mouse/scroll acceleration=%d result=%u\n",value,kr);
 CFRelease(data);CFRelease(dict);IOObjectRelease(service);IOObjectRelease(it);return kr?3:0;
}
