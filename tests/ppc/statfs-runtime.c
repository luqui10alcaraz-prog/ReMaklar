/* Real mounted filesystem ABI, same caller compiled i386/PPC. SPDX-License-Identifier: MIT */
#include <sys/types.h>
#include <sys/mount.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>
int main(void) {
    struct statfs a,b,volumes[32];int fd,n,j;
    if(sizeof(a)!=272)return 1;
    memset(&a,0xcc,sizeof(a));if(statfs("/usr/lib/libSystem.B.dylib",&a))return 2;
    fd=open("/usr/lib/libSystem.B.dylib",O_RDONLY);if(fd<0 || fstatfs(fd,&b))return 3;close(fd);
    if(a.f_bsize<=0 || a.f_iosize<=0 || a.f_blocks<=0 || !a.f_fstypename[0] || !a.f_mntonname[0] || !a.f_mntfromname[0])return 4;
    if(a.f_bsize!=b.f_bsize || a.f_iosize!=b.f_iosize || a.f_blocks!=b.f_blocks || a.f_type!=b.f_type || a.f_flags!=b.f_flags || memcmp(&a.f_fsid,&b.f_fsid,sizeof(a.f_fsid)) || strcmp(a.f_fstypename,b.f_fstypename) || strcmp(a.f_mntfromname,b.f_mntfromname))return 5;
    printf("FS bsize=%ld iosize=%ld blocks=%ld type=%d flags=%lx fsid=%x:%x owner=%u name=%s mount=%s from=%s\n",a.f_bsize,a.f_iosize,a.f_blocks,a.f_type,a.f_flags,a.f_fsid.val[0],a.f_fsid.val[1],a.f_owner,a.f_fstypename,a.f_mntonname,a.f_mntfromname);
    errno=0;if(statfs("/remaklar-009-absent",&b)!=-1 || errno!=ENOENT)return 6;
    errno=0;if(statfs("/usr/lib/libSystem.B.dylib",(struct statfs *)1)!=-1 || errno!=EFAULT)return 7;
    errno=0;if(fstatfs(-1,&b)!=-1 || errno!=EBADF)return 8;
    n=getfsstat(NULL,0,MNT_NOWAIT);if(n<1)return 9;
    n=getfsstat(volumes,sizeof(volumes),MNT_NOWAIT);if(n<1 || n>32)return 10;
    for(j=0;j<n;j++) {
        if(!volumes[j].f_fstypename[0] || !volumes[j].f_mntonname[0])return 11;
        printf("VOLUME type=%d fsid=%x:%x name=%s mount=%s from=%s\n",volumes[j].f_type,volumes[j].f_fsid.val[0],volumes[j].f_fsid.val[1],volumes[j].f_fstypename,volumes[j].f_mntonname,volumes[j].f_mntfromname);
    }
    errno=0;if(getfsstat((struct statfs *)1,sizeof(a),MNT_NOWAIT)!=-1 || errno!=EFAULT)return 12;
    puts("getfsstat real volumes count list EFAULT OK");
    puts("statfs PPC32 real volume direct fd ENOENT EFAULT EBADF OK");return 0;
}
