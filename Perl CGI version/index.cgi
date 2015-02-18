#!/usr/bin/perl -w

# エラーをブラウザに表示
use CGI;
use CGI::Carp qw/fatalsToBrowser warningsToBrowser/;
# DBIモジュール
use DBI;

$q = CGI -> new;

$db_host =       $ENV{'OPENSHIFT_MYSQL_DB_HOST'};
$db_username =   $ENV{'OPENSHIFT_MYSQL_DB_USERNAME'};
$db_password =   $ENV{'OPENSHIFT_MYSQL_DB_PASSWORD'};
$db_name =       $ENV{'OPENSHIFT_APP_NAME'};             # Default database name is same as application name

# DBへ接続
$db_source = "DBI:mysql:$db_name;host=$db_host";
$db_handle = DBI -> connect($db_source, $db_username, $db_password) or die $DBI::errstr;

check_login();

# ログインボタンが押されてきた場合は&loginへ
if($q->param('type') eq 'send'){
	&login;
} else {
	&html;
}

sub login{
	# 命令
	$sth = $db_handle->prepare( "select * from USER" );

	# 実行
	$sth->execute;

	while( @rows = $sth->fetchrow_array ){
		$login_id = $rows[0];
		$login_pw = $rows[1];

		# 認証
		if($q->param('name') eq $login_id && $q->param('pass') eq $login_pw){
			# 認証に成功した場合
			set_cookie();
			
			# 下記のURIへ飛ばす
			print $q->redirect(-uri => "top.html", -cookie => $cookie);
			exit 0;
		}
	}
	&html('Wrong username or password!');

	# 切断
	$db_handle->disconnect;
}

sub html{
	# 引数受取
	@msg = @_;

	# 出力
	print $q->header();
	print "<html>";
	print "<head>";
	print "<title>Login page</title>";
	print "</head>";
	print "<body>";
	print "<form action=index.cgi method=POST>";
	print "<input type=hidden name=\"type\" value=\"send\">";
	print "<table border=0 width=350>";
	print "<tr><td><center>";
	print "<table width=340>";
	print "<tr><td>Username </td><td><input type=text size=20 name=\"name\"></td></tr>";
	print "<tr><td>Password </td><td><input type=password size=20 name=\"pass\"></td></tr>";
	print "<tr><td> </td><td><input type=\"submit\" name=\"submit\" value=\"Login\"></td></tr>";
	foreach $str (@msg){
		print "<tr><td colspan=2><font color=red><b>$str</b></font></td></tr>";
	}
	print "</table>";
	print "</table>";
	print "<hr>";
	print "<a href=\"display.cgi\">View album (read-only)</a>";
	print "</body>";
	print "</html>";
}

sub set_cookie{
	# セッションIDをサーバ側で生成
	$sth = $db_handle->prepare( "insert into LOGIN values (UNIX_TIMESTAMP(NOW()))" );
	$sth->execute;
	$sth = $db_handle->prepare( "select * from LOGIN order by login_time DESC limit 1" );
	$sth->execute;
	@rows = $sth->fetchrow_array;
	$session_id = $rows[0];
			
	# セッションIDをクッキーにしてブラウザに保存
	$cookie = $q -> cookie(-name => 'session_id', -value => $session_id, -expires => '+1h');
}

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
		# クッキーが有効期間内である場合
		if ($now - $session_id < 3600) {
			print $q->redirect("top.html");
			exit 0;
		}
	}
}

exit;