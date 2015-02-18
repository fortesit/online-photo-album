#!/usr/bin/perl -w

use CGI;
use CGI::Carp qw ( warningsToBrowser fatalsToBrowser );
use Data::Dumper;

$q = CGI -> new;

$upload_dir = $ENV{'OPENSHIFT_DATA_DIR'};

# DBIモジュール
use DBI;

my $db_host =       $ENV{'OPENSHIFT_MYSQL_DB_HOST'};
my $db_username =   $ENV{'OPENSHIFT_MYSQL_DB_USERNAME'};
my $db_password =   $ENV{'OPENSHIFT_MYSQL_DB_PASSWORD'};
my $db_name =       $ENV{'OPENSHIFT_APP_NAME'};             # Default database name is same as application name

# DBへ接続
my $db_source = "DBI:mysql:$db_name;host=$db_host";
my $db_handle = DBI -> connect($db_source, $db_username, $db_password) or die $DBI::errstr;

check_login();

$post = {row => $q->param("row"), column => $q->param("column"), sort_by => $q->param("sort_by"), order => $q->param("order"), page => $q->param("page")};

# デフォルトパラメータを設定
if (!$q->param("row")) {
	$post->{row} = "2";
	$post->{column} = "4";
	$post->{page} = "1";
}
if (!$q->param("sort_by") || $q->param("sort_by") eq "not_selected") {
	$post->{sort_by} = "filename";
}
if (!$q->param("order") || $q->param("order") eq "not_selected") {
	$post->{order} = "ASC";
}

print $q->header();
print <<"__START_HTML";
<html>
<head>
<title>Album Display Interface</title>
</head>
<body>
<form action="display.cgi" method="POST">
__START_HTML

# ヘッダーを出力
sub print_header{
	print <<"__HEADER";
	Dimension <input type="number" name="row" min="1" max="9" value="$post->{row}" /> x <input type="number" name="column" min="1" max="9" value="$post->{column}" /> 
	<select name="sort_by">
		<option value="not_selected" selected>Sort by</option>
		<option value="size">File size</option>
		<option value="filename">Name</option>
		<option value="upload_time">Upload time</option>
	</select> 
	<select name="order">
		<option value="not_selected" selected>Order</option>
		<option value="ASC">Ascending</option>
		<option value="DESC">Descending</option>
	</select>
	<input type="submit" value="Change">
	<br>
__HEADER
}

# 写真のサムネ、チェックボックス、Removeボタンを出力
sub print_photo{
	# 写真数を抽出
	my $sth = $db_handle->prepare("select COUNT(*) from PHOTO");
	$sth->execute;
	@rows = $sth->fetchrow_array;
	$max_page = int(($rows[0] + ($post->{row} * $post->{column}) -1) / ($post->{row} * $post->{column}));
	if ($post->{page} > $max_page) {
		$post->{page} = $max_page;
	}
	$no_of_records = $post->{row} * $post->{column};
	$from = ($post->{page} - 1) * $post->{row} * $post->{column};

	# 写真情報を抽出
	my $sth = $db_handle->prepare("select * from PHOTO order by $post->{sort_by} $post->{order} limit $from, $no_of_records");
	$sth->execute;
	
	for ($k = 0; @rows = $sth->fetchrow_array; $k++) {
		$filename[$k] = $rows[0];
		$size[$k] = $rows[1];
		$upload_time[$k] = $rows[2];
		$description[$k] = $rows[3];
		$pathname[$k] = $rows[4];
	}

	print "<table border=0>";
	for ($i = 0, $index = 0; $i < $post->{row}; $i++) {
		print "<tr>";
		for ($j = 0; $j < $post->{column} && $k > 0; $j++, $index++, $k--) {
			print "<td><center><a href=\"/data/$filename[$index]\" target=\"_blank\"><img src=\"$pathname[$index]\" title=\"$description[$index]\"></a><br><br>";
			if (!$read_only) {
				print "<input type=checkbox name=\"$filename[$index]\" value=\"checked\"> ";
			}
			print "$filename[$index]</td><td></td>"
		}
		print "</tr><br>";
	}
	print "</table><br>";
	if (!$read_only) {
		print "<input type=submit value=\"Remove selected\"> ";
	}
}

# フッダーを出力
sub print_pagination{
	print "Page <input type=\"number\" name=\"page\" min=\"1\" max=\"$max_page\" value=\"$post->{page}\" /> of $max_page ";
	print "<input type=submit value=\"Go to page\">";
}

# 写真を削除
sub delete_photo{
	for $key ($q->param) {
		if ($key ne "row" && $key ne "column" && $key ne "sort_by" && $key ne "order" && $key ne "page") {
			`rm $upload_dir$key`;
			`rm ${upload_dir}thumbnail/${key}`;
			my $sth = $db_handle->prepare("delete from PHOTO where filename='$key'");
			$sth->execute;
		}
	}
}

delete_photo();
print_header();
print_photo();
print_pagination();

print "</form></body></html>";

# 切断
$db_handle->disconnect;

sub check_login{
	# ログインをチェック
	$sth = $db_handle->prepare( "select * from LOGIN order by login_time DESC limit 1" );
	$sth->execute;
	@rows = $sth->fetchrow_array;
	$session_id = $rows[0];
	$sth = $db_handle->prepare( "select UNIX_TIMESTAMP(NOW())" );
	$sth->execute;
	@rows = $sth->fetchrow_array;
	$now = $rows[0];
	
	if ($q->cookie('session_id') eq $session_id) {
		# クッキーが有効期間内でない場合
		if ($now - $session_id > 3600) {
			$read_only = 1;
		}
	} else {
		$read_only = 1;
	}
}