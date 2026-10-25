/* Original libSystem access() and indirect syscall ABI, with native oracle.
 * SPDX-License-Identifier: MIT */
#include <unistd.h>
#include <errno.h>
#include <stdio.h>
int main(void)
{
    const char *library="/usr/lib/libSystem.B.dylib";
    if(access(library,R_OK))return 1;
    if(syscall(33,library,R_OK))return 2;
    errno=0;
    if(access("/remaklar-008-deliberately-absent",F_OK)!=-1 || errno!=ENOENT)return 3;
    errno=0;
    if(syscall(33,"/remaklar-008-deliberately-absent",F_OK)!=-1 || errno!=ENOENT)return 4;
    puts("libSystem access direct indirect ENOENT OK");return 0;
}
