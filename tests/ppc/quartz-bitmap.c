/* Rendered by ORIGINAL CoreGraphics PPC. Own caller only, SPDX-License-Identifier: MIT.
 * Jaguar PPC32 public ABI declarations, for toolchains without CG headers. */
#include <stdio.h>
#include <stdlib.h>
typedef struct { float x,y; } CGPoint;
typedef struct { float width,height; } CGSize;
typedef struct { CGPoint origin; CGSize size; } CGRect;
typedef void *CGContextRef;
typedef void *CGColorSpaceRef;
extern CGColorSpaceRef CGColorSpaceCreateDeviceRGB(void);
extern void CGColorSpaceRelease(CGColorSpaceRef);
extern CGContextRef CGBitmapContextCreate(void *, unsigned long, unsigned long, unsigned long, unsigned long, CGColorSpaceRef, int);
extern void CGContextSetRGBFillColor(CGContextRef,float,float,float,float);
extern void CGContextFillRect(CGContextRef,CGRect);
extern void CGContextRelease(CGContextRef);
int main(int argc,char **argv)
{
    unsigned char pixels[64*48*4];
    unsigned int x,y;
    CGRect rect={{0,0},{64,48}};
    CGColorSpaceRef space=CGColorSpaceCreateDeviceRGB();
    CGContextRef context;
    FILE *file;
    if (!space) return 10;
    context=CGBitmapContextCreate(pixels,64,48,8,64*4,space,1); /* kCGImageAlphaPremultipliedLast */
    if (!context) return 11;
    CGContextSetRGBFillColor(context,0,0,1,1);
    CGContextFillRect(context,rect);
    rect.origin.x=16;rect.origin.y=12;rect.size.width=32;rect.size.height=24;
    CGContextSetRGBFillColor(context,1,0,0,1);
    CGContextFillRect(context,rect);
    CGContextRelease(context);CGColorSpaceRelease(space);
    file=fopen(argc>1?argv[1]:"/tmp/quartz.ppm","wb");
    if (!file) return 12;
    fprintf(file,"P6\n64 48\n255\n");
    for (y=0;y<48;y++) for (x=0;x<64;x++)
        if (fwrite(pixels+(y*64+x)*4,1,3,file)!=3) return 13;
    if (fclose(file)) return 14;
    puts("Quartz PPC bitmap OK");
    return 0;
}
