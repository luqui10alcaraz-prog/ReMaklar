/* Own Foundation test, no AppKit. SPDX-License-Identifier: MIT */
#import <objc/objc.h>
#include <stdio.h>
/* Public Jaguar method signatures: the install CD omits SDK headers. */
@interface NSObject
+ (id)alloc;
- (id)init;
- (void)release;
@end
@interface NSAutoreleasePool : NSObject
@end
@interface NSString : NSObject
+ (id)stringWithCString:(const char *)bytes;
- (BOOL)isEqualToString:(NSString *)other;
@end
@interface NSArray : NSObject
+ (id)arrayWithObjects:(id)first, ...;
- (NSString *)componentsJoinedByString:(NSString *)separator;
@end
int main(void)
{
    NSAutoreleasePool *pool=[[NSAutoreleasePool alloc] init];
    NSArray *values=[NSArray arrayWithObjects:[NSString stringWithCString:"Jaguar"],[NSString stringWithCString:"PPC"],nil];
    NSString *joined=[values componentsJoinedByString:[NSString stringWithCString:" "]];
    int good=[joined isEqualToString:[NSString stringWithCString:"Jaguar PPC"]];
    if (good) puts("Foundation PPC OK");
    [pool release];
    return good?0:1;
}
