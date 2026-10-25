#!/usr/bin/perl
# Bounded original-process probe; keeps leader and descendant outcomes separate.
# SPDX-License-Identifier: MIT
use strict;
use POSIX qw(:sys_wait_h setsid);
my ($stem,@command)=@ARGV;
die 'usage: output-stem command ...' unless @command;
open COMMAND,'>',"$stem.command" or die $!; print COMMAND join(' ',@command),"\n";close COMMAND;
my $pid=fork();die $! unless defined $pid;
if(!$pid) {
    setsid()>=0 or die "setsid: $!";
    open STDOUT,'>',"$stem.stdout" or die $!;
    open STDERR,'>',"$stem.stderr" or die $!;
    exec @command;die "exec: $!";
}
my $timeout=0;
local $SIG{ALRM}=sub {$timeout=1;kill 9,-$pid;};
alarm 45;while(waitpid($pid,0)!=$pid) {} my $raw=$?;alarm 0;
# daemon() can exit its parent and setsid() can leave the original group.
# Discover only children recorded by this runtime, then verify their current
# executable in ps before waiting or terminating them.
my %children;
sub live_children {
    if(open TRACE,'<',"$stem.stderr") {
        local $/;my $data=<TRACE>;close TRACE;
        while($data =~ /fork real host_pid=\d+ child_pid=(\d+) branch=parent/g) {$children{$1}=1;}
    }
    my @live;
    open PS,'ps -axww |' or die $!;
    while(<PS>) {
        if(/^\s*(\d+)\s+\S+\s+\S+\s+\S+\s+(.*)$/ && $children{$1} && index($2,$command[0])>=0) {push @live,$1;}
    }
    close PS;return @live;
}
my $seconds=0;
my @live=live_children();
while((kill(0,-$pid) || @live) && $seconds<45) {sleep 1;$seconds++;@live=live_children();}
my $remaining=kill 0,-$pid;
kill 9,-$pid if $remaining;
kill 9,@live if @live;
open STATUS,'>',"$stem.status" or die $!;
print STATUS "leader_exit=",(($raw&127)?128+($raw&127):$raw>>8),"\ntimeout=$timeout\nremaining_group_after_leader=$remaining\ndescendant_seconds=$seconds\nremaining_detached_children=".scalar(@live)."\n";
close STATUS;
