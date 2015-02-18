#!/usr/bin/perl -w

use CGI;
use CGI::Carp qw ( warningsToBrowser fatalsToBrowser );
use Data::Dumper;

my $q = CGI -> new;
my $upload_dir = $ENV{'OPENSHIFT_DATA_DIR'};
my $repo_dir = $ENV{'OPENSHIFT_REPO_DIR'};

if (!$q->param("yes")) {
	exit 0;
}

print $q->header();
print <<"__START_HTML";
<html>
<head>
<title>Initialization</title>
</head>
<body>
__START_HTML

# ファイルを削除
`rm ${upload_dir}*`;
`rm ${upload_dir}thumbnail/*`;

# 実行権限を与える
`chmod +x ${repo_dir}*`;

print "Clean storage...Done<br>";

# DBIモジュール
use DBI;

my $db_host =       $ENV{'OPENSHIFT_MYSQL_DB_HOST'};
my $db_username =   $ENV{'OPENSHIFT_MYSQL_DB_USERNAME'};
my $db_password =   $ENV{'OPENSHIFT_MYSQL_DB_PASSWORD'};
my $db_name =       $ENV{'OPENSHIFT_APP_NAME'};             # Default database name is same as application name

# DBへ接続
my $db_source = "DBI:mysql:$db_name;host=$db_host";
my $db_handle = DBI -> connect($db_source, $db_username, $db_password) or die $DBI::errstr;

# テーブル、データベースを削除
my $sth = $db_handle->prepare( "drop table USER" );
$sth->execute;
my $sth = $db_handle->prepare( "drop table PHOTO" );
$sth->execute;
my $sth = $db_handle->prepare( "drop table LOGIN" );
$sth->execute;

# データベース、テーブルを作成
my $sth = $db_handle->prepare( "create table USER (name varchar(100), password varchar(100))" );
$sth->execute;
my $sth = $db_handle->prepare( "create table PHOTO (filename varchar(100), size int(10), upload_time datetime, description text(100), pathname varchar(200))" );
$sth->execute;
my $sth = $db_handle->prepare( "create table LOGIN (login_time int(15))" );
$sth->execute;
my $sth = $db_handle->prepare( "insert into USER values ('tywong', 'sosad')" );
$sth->execute;

print <<"__END_HTML";
Create Table...Done<br>
Task Finished!<br><hr>
<a href="index.cgi">Back to Login Interface</a>
</body></html>
__END_HTML

# 切断
$db_handle->disconnect;
