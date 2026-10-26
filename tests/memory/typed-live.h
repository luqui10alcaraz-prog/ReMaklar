/* Isolated live endian view. No mirrored storage. SPDX-License-Identifier: MIT */
#ifndef RM_TYPED_LIVE_H
#define RM_TYPED_LIVE_H
typedef unsigned int rm_u32;
typedef unsigned long long rm_u64;
enum { RM_NUMBER = 0, RM_HID_BITS = 1, RM_PAIR16 = 2, RM_BYTES = 3 };
struct rm_field { unsigned offset, size, kind; };
struct rm_view {
    volatile unsigned char *base;
    unsigned bytes;
    const struct rm_field *fields;
    unsigned count;
    int writable;
};
int rm_read(const struct rm_view *,unsigned,unsigned,rm_u64 *);
int rm_write(const struct rm_view *,unsigned,unsigned,rm_u64);
int rm_cas32(const struct rm_view *,unsigned,rm_u32,rm_u32,int *);
void rm_barrier(void);
#endif
