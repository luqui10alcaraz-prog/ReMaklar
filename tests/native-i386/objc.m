/* Classical Apple/NeXT runtime only. SPDX-License-Identifier: MIT */
#import <objc/Object.h>
#include "images.h"
typedef struct { int a, b, c, d, e; } ProbeResult;
@interface NativeBase : Object
- (int)value;
@end
@implementation NativeBase
- (int)value { return 40; }
@end
@interface NativeProbe : NativeBase
- (int)value;
- (ProbeResult)structure;
@end
@implementation NativeProbe
- (int)value { return [super value] + 2; }
- (ProbeResult)structure
{
    ProbeResult r = { 1, 2, 42, -7, 123456 };
    return r;
}
@end
int main(void)
{
    NativeProbe *object;
    ProbeResult r;
    if (native_images(1, 1)) return 90;
    object = [NativeProbe new];
    if (!object || [object value] != 42) return 1;
    puts("OBJC class dispatch super value=42");
    r = [object structure];
    if (r.a != 1 || r.b != 2 || r.c != 42 || r.d != -7 || r.e != 123456) return 2;
    [object free];
    puts("OBJC i386 structure and free OK");
    return 0;
}
