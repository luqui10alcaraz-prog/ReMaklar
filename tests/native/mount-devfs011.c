/* Native mount syscall helper: Darwin CD lacks /sbin/mount_devfs.
 * Exposes original kernel device nodes, with no substitute device contents.
 * SPDX-License-Identifier: MIT */
#include <sys/param.h>
#include <sys/mount.h>
#include <stdio.h>
#include <errno.h>
#include <string.h>
int main(int argc,char **argv) {
 int result,saved;
 if(argc!=2)return 2;
 result=mount("devfs",argv[1],0,0);saved=errno;
 printf("native mount devfs path=%s result=%d errno=%d %s\n",argv[1],result,result?saved:0,result?strerror(saved):"OK");
 return result?1:0;
}
