/* SPDX-License-Identifier: MIT */
#include "images.h"
extern int remaklar_value(void);
int main(void)
{
    if (native_images(0, 0)) return 90;
    if (remaklar_value() != 42) return 1;
    if (NSIsSymbolNameDefined("_remaklar_nonexistent_007")) return 2;
    puts("DYLIB value=42 missing-symbol rejected");
    return 0;
}
