/* Observe actual loaded images, not just the architectures available on disk.
 * Own test code. SPDX-License-Identifier: MIT */
#include <stdio.h>
#include <string.h>
#include <mach/mach.h>
/* The Darwin CD omits mach-o/dyld.h. These declarations match the 32-bit
 * mach_header and image API in local Apple cctools-435 include/mach-o/{loader,
 * dyld}.h. No loader/runtime implementation is supplied by this test. */
struct native_mach_header {
    unsigned long magic;
    int cputype, cpusubtype;
    unsigned long filetype, ncmds, sizeofcmds, flags;
};
extern unsigned long _dyld_image_count(void);
extern struct native_mach_header *_dyld_get_image_header(unsigned long);
extern char *_dyld_get_image_name(unsigned long);
#define NATIVE_MH_MAGIC 0xfeedfaceUL
#define NATIVE_MH_DYLINKER 7
static int native_dyld(void)
{
    vm_address_t address = 0;
    vm_size_t size;
    vm_region_basic_info_data_t info;
    mach_msg_type_number_t count;
    mach_port_t object;
    while (1) {
        const struct native_mach_header *h;
        count = VM_REGION_BASIC_INFO_COUNT;
        if (vm_region(mach_task_self(), &address, &size, VM_REGION_BASIC_INFO,
                      (vm_region_info_t)&info, &count, &object)) break;
        if (object) mach_port_deallocate(mach_task_self(), object);
        if ((info.protection & VM_PROT_READ) && size >= sizeof(*h)) {
            h = (const struct native_mach_header *)address;
            if (h->magic == NATIVE_MH_MAGIC && h->filetype == NATIVE_MH_DYLINKER) {
                fprintf(stderr, "DYLD_MEMORY address=%08lx cpu=%d filetype=%lu\n",
                        (unsigned long)address, h->cputype, (unsigned long)h->filetype);
                return h->cputype == 7 ? 0 : 92;
            }
        }
        if (!size || address + size <= address) break;
        address += size;
    }
    return 93;
}
static int native_images(int need_objc, int need_cf)
{
    unsigned long i, count = _dyld_image_count();
    int objc = 0, cf = 0, system = 0;
    if (sizeof(unsigned long) != 4 || sizeof(struct native_mach_header) != 28) return 94;
    for (i = 0; i < count; ++i) {
        const struct native_mach_header *h = _dyld_get_image_header(i);
        const char *name = _dyld_get_image_name(i);
        fprintf(stderr, "IMAGE cpu=%d magic=%08lx path=%s\n",
                h->cputype, (unsigned long)h->magic, name);
        if (h->magic != NATIVE_MH_MAGIC || h->cputype != 7) return 90;
        if (strstr(name, "libobjc")) objc = 1;
        if (strstr(name, "CoreFoundation")) cf = 1;
        if (strstr(name, "libSystem")) system = 1;
    }
    if (!system || (need_objc && !objc) || (need_cf && !cf)) return 91;
    return native_dyld();
}
