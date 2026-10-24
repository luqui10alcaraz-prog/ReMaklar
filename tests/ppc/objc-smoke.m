/* First compiler-produced Objective-C test; no Foundation/Cocoa required.
 * Own source, SPDX-License-Identifier: MIT. Compile with the Jaguar NeXT ABI. */
#import <objc/Object.h>
#include <stdio.h>
@interface ReMaklarProbe : Object
- (int)value;
@end
@implementation ReMaklarProbe
- (int)value { return 42; }
@end
int main(void)
{
    ReMaklarProbe *object = [ReMaklarProbe new];
    int value = [object value];
    [object free];
    if (value != 42) return 1;
    puts("Objective-C PPC OK");
    return 0;
}
