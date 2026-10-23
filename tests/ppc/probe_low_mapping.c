/* Laboratory capability probe; link at a high address on Darwin.
 * SPDX-License-Identifier: MIT */
#include <stdio.h>
#include <errno.h>
#include <string.h>
#include <sys/mman.h>
#ifndef MAP_ANONYMOUS
#define MAP_ANONYMOUS MAP_ANON
#endif
int main(void) {
    void *p = mmap((void *)0x1000, 4096, PROT_READ | PROT_WRITE,
                   MAP_PRIVATE | MAP_ANONYMOUS | MAP_FIXED, -1, 0);
    if (p == MAP_FAILED) { fprintf(stderr, "mmap(0x1000): %s\n", strerror(errno)); return 1; }
    puts("mmap(0x1000): success");
    munmap(p, 4096); return 0;
}
