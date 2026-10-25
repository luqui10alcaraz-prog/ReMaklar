/* Same native query/errors, typed name result if supported by the volume. SPDX-License-Identifier: MIT */
#include <sys/types.h>
#include <sys/attr.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>
int main(void) {
    struct attrlist a;unsigned char buf[1024];int r,e;
    memset(&a,0,sizeof(a));a.bitmapcount=5;a.commonattr=ATTR_CMN_NAME;
    errno=0;r=getattrlist("/usr/lib/libSystem.B.dylib",&a,buf,sizeof(buf),0);e=errno;
    printf("getattrlist native-volume name result=%d errno=%d\n",r,r?e:0);
    if(r && e!=EOPNOTSUPP && e!=ENOTSUP)return 1;
    if(!r){attrreference_t *ref=(attrreference_t *)(buf+4);if(ref->attr_dataoffset<8 || ref->attr_length<1 || 4+ref->attr_dataoffset+ref->attr_length>sizeof(buf) || strcmp((char *)ref+ref->attr_dataoffset,"libSystem.B.dylib"))return 2;}
    errno=0;if(getattrlist("/remaklar-009-absent",&a,buf,sizeof(buf),0)!=-1 || errno!=ENOENT)return 3;
    a.bitmapcount=4;errno=0;if(getattrlist("/usr/lib/libSystem.B.dylib",&a,buf,sizeof(buf),0)!=-1 || errno!=EINVAL)return 4;
    puts("getattrlist real volume result ENOENT EINVAL OK");return 0;
}
