/* Original CF string/array and coherent timebase checks. SPDX-License-Identifier: MIT */
#include <CoreFoundation/CoreFoundation.h>
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
