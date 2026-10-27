/* A bounded prototype for i386 host / PPC logical fields, not a device model.
 * Atomic accesses act directly on the original mapped object.
 * SPDX-License-Identifier: MIT */
#include "typed-live.h"
#include <errno.h>

void rm_barrier(void)
{
    __asm__ __volatile__("lock; addl $0,0(%%esp)" : : : "memory", "cc");
}

static rm_u32 cas(volatile rm_u32 *p,rm_u32 old,rm_u32 value)
{
    __asm__ __volatile__("lock; cmpxchgl %2,%1"
        : "=a"(old), "=m"(*p) : "r"(value), "0"(old), "m"(*p) : "memory", "cc");
    return old;
}

static rm_u64 native_read(volatile unsigned char *p,unsigned size)
{
    if(size==1)return *p;
    if(size==2)return *(volatile unsigned short *)p;
    if(size==4)return *(volatile rm_u32 *)p;
    /* cmpxchg8b supplies one coherent read even on an i386 ABI. */
    {
        rm_u32 lo=0,hi=0,low=0;
        /* Darwin GCC2 reserves ebx for PIC. Borrow it without clobbering the
         * caller's PIC base; force the object address into edi. */
        __asm__ __volatile__("xchgl %%ebx,%2; .byte 0xf0,0x0f,0xc7,0x0f; xchgl %%ebx,%2"
            : "=a"(lo), "=d"(hi), "=S"(low)
            : "D"(p), "c"(0), "0"(lo), "1"(hi), "2"(low) : "memory", "cc");
        return ((rm_u64)hi<<32)|lo;
    }
}

static int native_cas(volatile unsigned char *p,unsigned size,rm_u64 old,rm_u64 value)
{
    unsigned char ok;
    if(size==1) {
        rm_u32 x=(unsigned char)old;
        __asm__ __volatile__("lock; cmpxchgb %b3,%1"
            : "=a"(x), "=m"(*p) : "0"(x), "q"((rm_u32)value), "m"(*p) : "memory","cc");
        return (unsigned char)x==(unsigned char)old;
    } else if(size==2) {
        rm_u32 x=(unsigned short)old;
        __asm__ __volatile__("lock; cmpxchgw %w3,%1"
            : "=a"(x), "=m"(*(volatile unsigned short *)p)
            : "0"(x), "r"((rm_u32)value), "m"(*(volatile unsigned short *)p) : "memory","cc");
        return (unsigned short)x==(unsigned short)old;
    } else if(size==4) return cas((volatile rm_u32 *)p,old,value)==(rm_u32)old;
    else {
        rm_u32 lo=old,hi=old>>32,low=value;
        __asm__ __volatile__("xchgl %%ebx,%3; .byte 0xf0,0x0f,0xc7,0x0f; xchgl %%ebx,%3; sete %0"
            : "=m"(ok), "=a"(lo), "=d"(hi), "=S"(low)
            : "D"(p), "c"((rm_u32)(value>>32)), "1"(lo), "2"(hi), "3"(low) : "memory","cc");
    }
    return ok;
}

static const struct rm_field *field(const struct rm_view *v,unsigned pos,unsigned n)
{
    unsigned i;
    if(!n || n>8 || pos>v->bytes || n>v->bytes-pos)return 0;
    for(i=0;i<v->count;i++) {
        const struct rm_field *f=v->fields+i;
        if(pos>=f->offset && pos-f->offset<f->size && n<=f->size-(pos-f->offset)) {
            if((f->size!=1 && f->size!=2 && f->size!=4 && f->size!=8) ||
               f->offset%(f->size==8?4:f->size) || f->offset>v->bytes || f->size>v->bytes-f->offset ||
               (f->kind!=RM_NUMBER && !(f->kind==RM_HID_BITS && f->size==4) && !(f->kind==RM_PAIR16 && f->size==4) && !(f->kind==RM_BYTES && (f->size==2 || f->size==4 || f->size==8))))return 0;
            return f;
        }
    }
    return 0;
}

static rm_u64 logical(const struct rm_field *f,rm_u64 x)
{
    /* PPC's first declared bitfield occupies the MSBs, i386's the LSBs. */
    if(f->kind==RM_HID_BITS)return (rm_u32)((((rm_u32)x&0x07ffffffU)<<5)|
        (((rm_u32)x>>31)&1)|(((rm_u32)x>>29)&2)|(((rm_u32)x>>27)&4)|
        (((rm_u32)x>>25)&8)|(((rm_u32)x>>23)&16));
    if(f->kind==RM_PAIR16)return (rm_u32)(((rm_u32)x>>16)|((rm_u32)x<<16));
    if(f->kind==RM_BYTES){rm_u64 result=0;unsigned i;for(i=0;i<f->size;i++){result=(result<<8)|(x&255);x>>=8;}return result;}
    return x;
}
static rm_u64 physical(const struct rm_field *f,rm_u64 x)
{
    if(f->kind==RM_HID_BITS)return (rm_u32)(((rm_u32)x>>5)|
        (((rm_u32)x&1)<<31)|(((rm_u32)x&2)<<29)|(((rm_u32)x&4)<<27)|
        (((rm_u32)x&8)<<25)|(((rm_u32)x&16)<<23));
    if(f->kind==RM_PAIR16 || f->kind==RM_BYTES)return logical(f,x);
    return x;
}

int rm_read(const struct rm_view *v,unsigned pos,unsigned n,rm_u64 *out)
{
    const struct rm_field *f=field(v,pos,n);rm_u64 x,mask;
    if(!f)return EINVAL;
    /* cmpxchg8b requires write permission even when used as a read. The
     * prototype must reject this rather than fault or weaken protections. */
    if(f->size==8 && !v->writable)return EACCES;
    x=logical(f,native_read(v->base+f->offset,f->size));
    mask=n==8?~(rm_u64)0:(((rm_u64)1<<(8*n))-1);
    *out=(x>>(8*(f->size-(pos-f->offset)-n)))&mask;
    return 0;
}

int rm_write(const struct rm_view *v,unsigned pos,unsigned n,rm_u64 value)
{
    const struct rm_field *f=field(v,pos,n);rm_u64 old,x,mask;unsigned shift;
    if(!v->writable)return EACCES;
    if(!f)return EINVAL;
    shift=8*(f->size-(pos-f->offset)-n);
    mask=n==8?~(rm_u64)0:(((rm_u64)1<<(8*n))-1);
    do {
        old=native_read(v->base+f->offset,f->size);
        x=(logical(f,old)&~(mask<<shift))|((value&mask)<<shift);
    } while(!native_cas(v->base+f->offset,f->size,old,physical(f,x)));
    return 0;
}

int rm_cas32(const struct rm_view *v,unsigned pos,rm_u32 old,rm_u32 value,int *ok)
{
    const struct rm_field *f=field(v,pos,4);
    if(!v->writable)return EACCES;
    if(!f || pos!=f->offset || f->size!=4)return EINVAL;
    *ok=cas((volatile rm_u32 *)(v->base+pos),physical(f,old),physical(f,value))==(rm_u32)physical(f,old);
    return 0;
}
