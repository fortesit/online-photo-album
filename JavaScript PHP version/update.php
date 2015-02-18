<?php

	/* Connect the database */
	$dbServer = $_ENV['OPENSHIFT_MYSQL_DB_HOST'];
	$dbUser = $_ENV['OPENSHIFT_MYSQL_DB_USERNAME'];
	$dbPassword = $_ENV['OPENSHIFT_MYSQL_DB_PASSWORD'];
	$dbName = $_ENV['OPENSHIFT_APP_NAME'];

	$link = mysql_connect($dbServer, $dbUser, $dbPassword);
	if (!$link) {
	    die('Database connection failed: ' . mysql_error()); // Prevent printing other things below
	}
	mysql_select_db($dbName, $link);
	
	if ($_SERVER["HTTP_DESCRIPTION"]) {
		$sql = sprintf("UPDATE PHOTO SET description = '%s' WHERE filename = '%s'", mysql_real_escape_string($_SERVER['HTTP_DESCRIPTION']), mysql_real_escape_string($_SERVER['HTTP_FILE_NAME']));
		mysql_query($sql, $link);
	}
	
	if ($_SERVER["HTTP_DELETE"]) {
		unlink("img/" . $_SERVER['HTTP_FILE_NAME']);
		$sql = sprintf("DELETE FROM PHOTO WHERE filename = '%s'", mysql_real_escape_string($_SERVER['HTTP_FILE_NAME']));
		mysql_query($sql, $link);
	}
?>