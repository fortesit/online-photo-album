#!/usr/bin/perl -w

use CGI;
use CGI::Carp qw ( warningsToBrowser fatalsToBrowser );
use Data::Dumper;

$q = CGI -> new;

# クッキーを削除
$cookie = $q -> cookie(-name => 'session_id', -value => '', -expires => '-1h');

print $q->redirect(-uri => "index.cgi", -cookie => $cookie);

