/* Public CF 32-bit ABI declarations, no implementation or Foundation.
 * Header provenance and validation are recorded in the milestone report.
 * SPDX-License-Identifier: MIT */
#include "images.h"
#include <mach/mach_time.h>
#include <unistd.h>
typedef long CFIndex;
typedef unsigned long CFStringEncoding;
typedef unsigned char Boolean;
typedef const void *CFAllocatorRef;
typedef const void *CFTypeRef;
typedef const void *CFStringRef;
typedef const void *CFArrayRef;
typedef void *CFMutableArrayRef;
typedef struct {
    CFIndex version;
    const void *(*retain)(CFAllocatorRef, const void *);
    void (*release)(CFAllocatorRef, const void *);
    CFStringRef (*copyDescription)(const void *);
    Boolean (*equal)(const void *, const void *);
} CFArrayCallBacks;
extern const CFArrayCallBacks kCFTypeArrayCallBacks;
extern CFStringRef CFStringCreateWithCString(CFAllocatorRef,const char *,CFStringEncoding);
extern Boolean CFStringGetCString(CFStringRef,char *,CFIndex,CFStringEncoding);
extern CFIndex CFStringGetLength(CFStringRef);
extern CFMutableArrayRef CFArrayCreateMutable(CFAllocatorRef,CFIndex,const CFArrayCallBacks *);
extern void CFArrayAppendValue(CFMutableArrayRef,const void *);
extern CFIndex CFArrayGetCount(CFArrayRef);
extern const void *CFArrayGetValueAtIndex(CFArrayRef,CFIndex);
extern CFTypeRef CFRetain(CFTypeRef);
extern void CFRelease(CFTypeRef);
extern double CFAbsoluteTimeGetCurrent(void);
#define UTF8 0x08000100UL
int main(void)
{
    const char *strings[] = { "", "Jaguar i386", "Espa\303\261ol \342\230\203" };
    CFIndex lengths[] = { 0, 11, 9 };
    CFMutableArrayRef array;
    CFStringRef s;
    int i;
    char buffer[80];
    double t0, t1;
    unsigned long long a, b;
    mach_timebase_info_data_t info;
    if (native_images(0, 1)) return 90;
    array = CFArrayCreateMutable(0, 0, &kCFTypeArrayCallBacks);
    if (!array) return 1;
    for (i=0; i<3; ++i) {
        s = CFStringCreateWithCString(0, strings[i], UTF8);
        if (!s || CFStringGetLength(s) != lengths[i]) return 2;
        if (CFRetain(s) != s) return 3;
        CFRelease(s);
        CFArrayAppendValue(array, s);
        CFRelease(s); /* Array must retain the element after our ownership ends. */
    }
    if (CFArrayGetCount(array) != 3) return 4;
    for (i=0; i<3; ++i) {
        s = CFArrayGetValueAtIndex(array, i);
        if (!CFStringGetCString(s, buffer, sizeof(buffer), UTF8) || strcmp(buffer, strings[i])) return 5;
    }
    s = CFArrayGetValueAtIndex(array, 1);
    if (CFStringGetCString(s, buffer, 1, UTF8)) return 6;
    CFRelease(array);
    t0 = CFAbsoluteTimeGetCurrent(); a = mach_absolute_time();
    usleep(20000);
    t1 = CFAbsoluteTimeGetCurrent(); b = mach_absolute_time();
    if (t0 <= 0 || t1 < t0 || b <= a || mach_timebase_info(&info) || !info.numer || !info.denom) return 7;
    puts("CF i386 UTF8 empty nonASCII array retain release time OK");
    return 0;
}
