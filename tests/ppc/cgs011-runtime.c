/* Diagnostic caller of the unchanged Jaguar CoreGraphics binary.
 * Signature verified against CGSNewConnection's original PPC disassembly. */
#include <stdio.h>
extern int CGSNewConnection(const void *,unsigned *);
extern int CGSReleaseConnection(unsigned);
int main(void) {
 unsigned connection=0;int result=CGSNewConnection(0,&connection);
 printf("original CGSNewConnection result=%d connection=%u\n",result,connection);
 if(result || !connection)return 1;
 result=CGSReleaseConnection(connection);
 printf("original CGSReleaseConnection result=%d\n",result);
 return result!=0;
}
