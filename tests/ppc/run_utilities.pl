#!/usr/bin/perl
# Byte-exact process tests; compatible with the stock Darwin 6 Perl.
# SPDX-License-Identifier: MIT
use strict;
use POSIX qw(:sys_wait_h);
my ($exe, $root, $vectors, $out) = @ARGV;
die "usage: $0 executor guest-root vectors output-directory\n" unless defined $out;
mkdir $out unless -d $out;
open CASES, '<', $vectors or die "$vectors: $!";
open RESULTS, '>', "$out/results.tsv" or die $!;
my ($failed, $count) = (0, 0);
sub bytes { return $_[0] eq '-' ? '' : pack('H*', $_[0]); }
sub slurp {
    my ($path) = @_;
    open IN, '<', $path or die "$path: $!"; binmode IN;
    local $/; my $data = <IN>; close IN; return defined $data ? $data : '';
}
while (<CASES>) {
    chomp;
    my ($id, $program, $expected, $entry, $input, $output, $diagnostic, @args) = split /\t/;
    die "bad vector" unless $id =~ /^[a-z0-9-]+$/ && $program =~ /^(echo|cat)$/;
    open INPUT, '>', "$out/$id.stdin" or die $!; binmode INPUT;
    print INPUT bytes($input); close INPUT;
    my @command = ($exe, '--root', $root, "$root/bin/$program", map { bytes($_) } @args);
    my $pid = fork(); die "fork: $!" unless defined $pid;
    if (!$pid) {
        open STDIN, '<', "$out/$id.stdin" or die $!;
        open STDOUT, '>', "$out/$id.stdout" or die $!;
        open STDERR, '>', "$out/$id.stderr" or die $!;
        binmode STDIN; binmode STDOUT; binmode STDERR;
        $ENV{LC_ALL} = $ENV{LANG} = 'C'; $ENV{TZ} = 'UTC';
        delete $ENV{REMAKLAR_TRACE};
        exec @command; die "exec: $!";
    }
    my $timed_out = 0;
    local $SIG{ALRM} = sub { $timed_out = 1; kill 9, $pid; };
    alarm 90; while (waitpid($pid, 0) != $pid) { }
    my $raw = $?; alarm 0;
    my $status = ($raw & 127) ? 128 + ($raw & 127) : $raw >> 8;
    my $stdout = slurp("$out/$id.stdout"); my $stderr = slurp("$out/$id.stderr");
    my $marker = "startup: entered original executable at $entry";
    my $startup_count = () = $stderr =~ /\Q$marker\E/g;
    my $ok = !$timed_out && $status == $expected && $stdout eq bytes($output) &&
        $startup_count == 1 && index($stderr, 'probe-main:') < 0 &&
        index($stderr, 'unsupported') < 0 && index($stderr, 'unhandled host') < 0 &&
        $stderr =~ / r0=1 / &&
        index($stderr, "guest open $root/usr/lib/libSystem.B.dylib") >= 0 &&
        index($stderr, "guest open $root/usr/lib/system/libmathCommon.A.dylib") >= 0 &&
        index($stderr, bytes($diagnostic)) >= 0;
    my $line = ($ok ? 'PASS' : 'FAIL')."\t$id\texit=$status expected=$expected\tbytes=".length($stdout)."\n";
    print $line; print RESULTS $line;
    $failed++ unless $ok; $count++;
}
print RESULTS "cases=$count failed=$failed\n"; close RESULTS;
print "cases=$count failed=$failed\n";
exit($failed ? 1 : 0);
