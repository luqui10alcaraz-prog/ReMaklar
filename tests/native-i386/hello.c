/* SPDX-License-Identifier: MIT */
#include "images.h"
int main(void)
{
    int r = native_images(0, 0);
    if (r) return r;
    puts("C i386 normal startup OK");
    return 0;
}
