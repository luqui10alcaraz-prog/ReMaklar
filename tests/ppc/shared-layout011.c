/* Compile against the guest's actual Jaguar/Darwin headers on both ABIs.
 * SPDX-License-Identifier: MIT */
#define _IOKIT_IOKITLIB_H
#define _IOKIT_IOHIDLIB_H
#include <stdio.h>
#include <stddef.h>
#include <IOKit/graphics/IOFramebufferShared.h>
#include <IOKit/hidsystem/IOHIDShared.h>
#define SHOW(t,f) printf(#t "." #f "=%u\n",(unsigned)offsetof(t,f))
int main(void)
{
 EvGlobals globals;
 unsigned *bits;
 printf("StdFBShmem=%u EvOffsets=%u EvGlobals=%u NXEQElement=%u NXEvent=%u NXEventData=%u\n",
 (unsigned)sizeof(StdFBShmem_t),(unsigned)sizeof(EvOffsets),(unsigned)sizeof(EvGlobals),
 (unsigned)sizeof(NXEQElement),(unsigned)sizeof(NXEvent),(unsigned)sizeof(NXEventData));
 SHOW(StdFBShmem_t,version);SHOW(StdFBShmem_t,vblTime);SHOW(StdFBShmem_t,cursorSize);SHOW(StdFBShmem_t,cursor);
 SHOW(EvGlobals,cursorLoc);SHOW(EvGlobals,version);SHOW(EvGlobals,movedMask);
 SHOW(EvGlobals,waitThreshold);SHOW(EvGlobals,lleq);SHOW(NXEQElement,event);
 SHOW(NXEvent,time);SHOW(NXEvent,data);SHOW(NXTabletProximityData,uniqueID);
 globals.mouseRectValid=0;globals.wantPressure=0;globals.wantPrecision=0;
 globals.dontWantCoalesce=0;globals.dontCoalesce=0;globals.reserved=0;
 globals.mouseRectValid=1;
 bits=(unsigned *)((char *)&globals+offsetof(EvGlobals,movedMask)-4);
 printf("mouseRectValid-mask=%08x\n",*bits);
 return 0;
}
