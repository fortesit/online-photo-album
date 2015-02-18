#!/usr/bin/perl -w

use CGI;
use CGI::Carp qw ( warningsToBrowser fatalsToBrowser );
use Data::Dumper;

my $q = CGI -> new;

my $upload_dir = $ENV{'OPENSHIFT_DATA_DIR'};

my $filename = $q->param("filename");
my $description = $q->param("description");
my $ext = $q->param("ext");
my $totalBytes = $q->param("totalBytes");
my $answer = $q->param("answer");
my $new_filename = $q->param("new_filename");
my $file = $q->upload('filename');

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

# descriptionの特殊文字の変換
$description =~ s/&/&amp;/g;
$description =~ s/</&lt;/g;
$description =~ s/>/&gt;/g;
$description =~ s/"/&quot;/g;
$description =~ s/'/&#39;/g;

# Overwriteの場合
if ($answer eq "overwrite") {
	# レコードを削除
	my $sth = $db_handle->prepare( "delete from PHOTO where filename='$filename';" );
	$sth->execute;
	`rm $upload_dir$filename`;
	`rm ${upload_dir}thumbnail/${filename}`;
	`mv $upload_dir.$filename $upload_dir$filename`;
	goto FINISH;
}

# Renameの場合
if ($answer eq "rename") {
	$new_filename = $new_filename . "." . $ext;
	`mv $upload_dir.$filename $upload_dir$new_filename`;
	$filename = $new_filename;
	goto FINISH;
}

# Cancelの場合
if ($answer eq "cancel") {
	# 切断
	$db_handle->disconnect;
	print $q->redirect("upload_form.html");
	exit 0;
}

$_ = $filename; 
my ($name, $ext) = /([A-Za-z0-9-_]+).([A-Za-z0-9-_]+)/;

if ($ext eq "JPEG" || $ext eq "jpeg") {
	goto DIE;
}

# 重複ファイルを検出
my $sth = $db_handle->prepare( "select COUNT(*) from PHOTO where filename='$filename';" );
$sth->execute;

$file_count=$sth->fetchrow_array;
if ($file_count ne "0") {
	$old_filename = $filename;
	$filename = '.' . $filename;
}

# ファイルの読みエラー

if (! open(OUTFILE, "> $upload_dir$filename") ) {
	# 切断
	$db_handle->disconnect;
    die("Can't open $filename for writing - $!");
}

my $ret = 0;
if (!$totalBytes) {
	my $totalBytes = 0;
}
my $buffer = "";

binmode($filename);

while ( $ret = read($file, $buffer, 1024) ) {
    print OUTFILE $buffer;
    $totalBytes += $ret;
}

# ファイルサイズが大きすぎる
if ($totalBytes > 1000000) {
	`rm $upload_dir$filename`;
	print $q -> header();
    print <<__TOO_BIG_FAIL;
<html>
<body>
File too large<br>
<a href="upload_form.html">Back</a><br>
</body>
</html>
__TOO_BIG_FAIL
	# 切断
	$db_handle->disconnect;
    exit 0;
}

close(OUTFILE);

if ($file_count ne "0") {
	print $q->header();
print <<"__START_HTML";
<html>
<head>
<title>Duplicated file</title>
</head>
<body>
<form action="upload.cgi" method="POST">
	<input type="hidden" name="filename" value="$old_filename"/>
	<input type="hidden" name="description" value="$description"/> 
	<input type="hidden" name="ext" value="$ext"/> 
	<input type="hidden" name="totalBytes" value="$totalBytes"/> 
    <input type="radio" name="answer" value="overwrite" checked/> Overwrite the existing file "$old_filename"
    <br />
    <input type="radio" name="answer" value="rename"/> Rename the uploading file.
    <br />
    New filename <input type="text" name="new_filename"/> .$ext
    <br />
    <input type="radio" name="answer" value="cancel" /> Cancel the current upload.
    <br />
    <input type="submit" value="Proceed" />
</form>
</body>
</html>
__START_HTML
	exit 0;
}

# ファイルのフォーマットエラー

my $out1 = `identify $upload_dir$filename`;
my @array1 = split(/ /, $out1);
if (@array1[1] ne "JPEG" && @array1[1] ne "PNG" && @array1[1] ne "GIF") {
DIE:
	`rm $upload_dir$filename`;
	print $q -> header();
	print <<__NOT_SUPPORT_FAIL;
<html>
<body>
$filename is not in supported format(JPG/PNG/GIF)<br>
<a href="upload_form.html">Back</a><br>
</body>
</html>
__NOT_SUPPORT_FAIL
	# 切断
	$db_handle->disconnect;
	exit 0;
}

FINISH:
# レコードを挿入
my $sth = $db_handle->prepare( "insert into PHOTO (filename, size, upload_time, description, pathname) VALUES ('$filename', '$totalBytes', NOW(), '$description', '/data/thumbnail/${filename}')" );
$sth->execute;

# サムネを転換
`convert $upload_dir${filename} -resize 100x ${upload_dir}thumbnail/${filename}`;

# 切断
$db_handle->disconnect;

# 問題なく成功した場合、結果を出力

print $q->header();
print <<"__START_HTML";
<html>
<head>
<title>Upload Successful</title>
</head>
<body>
__START_HTML

print "Your file has been uploaded (Size = $totalBytes bytes)<br />"; 
print "<h3>Image</h3><img src='../data/$filename'><br>"; 
print "<a href=\"upload_form.html\">Back</a><br>";
print "</body></html>";

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
			print $q->redirect("index.cgi");
			exit 0;
		}
	} else {
		print $q->redirect("index.cgi");
		exit 0;
	}
}
