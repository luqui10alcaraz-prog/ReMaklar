/* Cross the old automatic-export ceiling, then exercise real extended rights. */
#include <mach/mach.h>
#include <mach/mach_time.h>
#include <stdio.h>
#include <string.h>
extern mach_port_t mk_timer_create(void);
extern kern_return_t mk_timer_destroy(mach_port_t);
extern kern_return_t mk_timer_arm(mach_port_t,unsigned long long);
typedef struct {mach_msg_header_t h;unsigned long long created,armed,posted;} timer_msg;
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL capacity line=%d\n",__LINE__);return 1;}}while(0)
int main(void)
{
 mach_port_t p[3],port,set,retired=0;mach_port_type_t type;mach_port_urefs_t refs;unsigned i;mach_port_name_array_t members;mach_msg_type_number_t count;
 mach_port_limits_t limits;mach_port_limits_t result;union{timer_msg t;unsigned char bytes[128];} msg;unsigned long long deadline;
 for(i=0;i<4100;i++){
  CHECK(!mach_port_allocate(mach_task_self(),MACH_PORT_RIGHT_RECEIVE,&port));if(!i)retired=port;
  CHECK(!mach_port_destroy(mach_task_self(),port));
  if(!((i+1)%1000)){printf("real allocate/destroy cycles=%u\n",i+1);fflush(stdout);}
 }
 CHECK(mach_port_type(mach_task_self(),retired,&type)==KERN_INVALID_NAME);
 for(i=0;i<3;i++)CHECK(!mach_port_allocate(mach_task_self(),MACH_PORT_RIGHT_RECEIVE,p+i));
 CHECK(!mach_port_rename(mach_task_self(),p[0],0x56000100U));p[0]=0x56000100U;
 for(i=0;i<2;i++)CHECK(!mach_port_insert_right(mach_task_self(),p[i],p[i],MACH_MSG_TYPE_MAKE_SEND));
 CHECK(mach_port_rename(mach_task_self(),p[1],p[1])==KERN_NAME_EXISTS);
 CHECK(mach_port_rename(mach_task_self(),p[2],p[1])==KERN_NAME_EXISTS);
 CHECK(!mach_port_get_refs(mach_task_self(),p[1],MACH_PORT_RIGHT_SEND,&refs)&&refs==1);
 limits.mpl_qlimit=3;CHECK(!mach_port_set_attributes(mach_task_self(),p[1],MACH_PORT_LIMITS_INFO,(mach_port_info_t)&limits,MACH_PORT_LIMITS_INFO_COUNT));
 count=MACH_PORT_LIMITS_INFO_COUNT;CHECK(!mach_port_get_attributes(mach_task_self(),p[1],MACH_PORT_LIMITS_INFO,(mach_port_info_t)&result,&count)&&result.mpl_qlimit==3);
 CHECK(!mach_port_allocate(mach_task_self(),MACH_PORT_RIGHT_PORT_SET,&set));
 CHECK(!mach_port_move_member(mach_task_self(),p[0],set)&&!mach_port_move_member(mach_task_self(),p[1],set));
 CHECK(!mach_port_get_set_status(mach_task_self(),set,&members,&count)&&count==2);
 CHECK((members[0]==p[0]&&members[1]==p[1])||(members[1]==p[0]&&members[0]==p[1]));CHECK(!vm_deallocate(mach_task_self(),(vm_address_t)members,count*sizeof(*members)));
 memset(&msg,0,sizeof(msg));msg.t.h.msgh_bits=MACH_MSGH_BITS(MACH_MSG_TYPE_COPY_SEND,0);msg.t.h.msgh_remote_port=p[1];msg.t.h.msgh_size=24;msg.t.h.msgh_id=8101;
 CHECK(!mach_msg(&msg.t.h,MACH_SEND_MSG,24,0,0,0,0));CHECK(!mach_msg(&msg.t.h,MACH_RCV_MSG|MACH_RCV_TIMEOUT,0,sizeof(msg),set,1000,0));CHECK(msg.t.h.msgh_id==8101&&msg.t.h.msgh_local_port==p[1]);
 for(i=0;i<3;i++){CHECK(!mach_port_destroy(mach_task_self(),p[i]));CHECK(mach_port_type(mach_task_self(),p[i],&type)==KERN_INVALID_NAME);}CHECK(!mach_port_destroy(mach_task_self(),set));
 port=mk_timer_create();CHECK(port);deadline=mach_absolute_time()+100000000ULL;CHECK(!mk_timer_arm(port,deadline));memset(&msg,0,sizeof(msg));
 CHECK(!mach_msg(&msg.t.h,MACH_RCV_MSG|MACH_RCV_TIMEOUT,0,sizeof(msg),port,3000,0));CHECK(msg.t.h.msgh_size==48&&msg.t.armed==deadline&&msg.t.created<=deadline&&msg.t.posted>=deadline);CHECK(!mk_timer_destroy(port));
 puts("real extended capabilities: 4100 cycles, retired names, rename/collision, send refs, limits, port-set delivery, destroy and typed timer PASS");return 0;
}
