/* Original CF string/array and coherent timebase checks. SPDX-License-Identifier: MIT */
/* Public PPC32 declarations: the Darwin CD's umbrella headers reference SDK
 * files it does not ship. These declarations contain no implementation. */
typedef const void *CFStringRef;
typedef void *CFMutableArrayRef;
typedef long CFIndex;
extern const struct { long version; void *retain,*release,*description,*equal; } kCFTypeArrayCallBacks;
extern CFStringRef CFStringCreateWithCString(const void *,const char *,unsigned long);
extern CFMutableArrayRef CFArrayCreateMutable(const void *,CFIndex,const void *);
extern void CFArrayAppendValue(CFMutableArrayRef,const void *);
extern CFIndex CFArrayGetCount(const void *);
extern const void *CFArrayGetValueAtIndex(const void *,CFIndex);
extern unsigned char CFStringGetCString(CFStringRef,char *,CFIndex,unsigned long);
extern void CFRelease(const void *);
#define kCFStringEncodingUTF8 0x08000100UL
#include <mach/mach_time.h>
#include <stdio.h>
#include <string.h>
int main(void)
{
    CFStringRef text=CFStringCreateWithCString(NULL,"Jaguar PPC",kCFStringEncodingUTF8);
    CFMutableArrayRef array=CFArrayCreateMutable(NULL,0,&kCFTypeArrayCallBacks);
    char buffer[64]; mach_timebase_info_data_t info;
    unsigned long long before,after;
    if (!text || !array) return 1;
    CFArrayAppendValue(array,text);
    if (CFArrayGetCount(array)!=1 || !CFStringGetCString((CFStringRef)CFArrayGetValueAtIndex(array,0),buffer,sizeof(buffer),kCFStringEncodingUTF8) || strcmp(buffer,"Jaguar PPC")) return 2;
    before=mach_absolute_time(); after=mach_absolute_time();
    if (mach_timebase_info(&info) || !info.numer || !info.denom || after<before) return 3;
    CFRelease(array);CFRelease(text);
    puts("CoreFoundation PPC OK");
    return 0;
}
