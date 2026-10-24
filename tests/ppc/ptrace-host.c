/* Native Darwin oracle for the private marker calls. SPDX-License-Identifier: MIT */
#include <sys/types.h>
#include <sys/ptrace.h>
#include <errno.h>
#include <stdio.h>
int main(void)
{
    int r, error, failed = 0;
    int requests[2] = {0xc000, 0xb000};
    int i;
    for (i = 0; i < 2; i++) {
        errno = 0;
        r = ptrace(requests[i], 0, (char *)0, 0);
        error = errno;
        printf("request=%x result=%d errno=%d\n", requests[i], r, error);
        if (r != -1 || error != EPERM) failed = 1;
    }
    return failed;
}
