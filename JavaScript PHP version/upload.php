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
	
	$raw_data = file_get_contents('php://input');
	$data = base64_decode($raw_data); // decode the result
	$filesize = strlen($data);
	file_put_contents("img/" . $_SERVER['HTTP_FILE_NAME'], $data);
	
	$json = array('error_msg'=>'', 'files'=>array("filename"=>'', "description"=>''), 'file_count'=>0, );
	$path_parts = pathinfo($_SERVER['HTTP_FILE_NAME']);
	
	/* Get file names*/
	$sql = sprintf("SELECT * FROM PHOTO");
	$query = mysql_query($sql, $link);
	$i = 0;
	while ($row = mysql_fetch_object($query)) {
	    $json['files'][$i]["filename"] = $row->filename;
	    $json['files'][$i]["description"] = $row->description;
	    $i++;
	}
	$json['file_count'] = $i;
	
	/* Check file type */
	if ((mime_content_type("img/" . $_SERVER['HTTP_FILE_NAME']) != "image/jpeg" && mime_content_type("img/" . $_SERVER['HTTP_FILE_NAME']) != "image/gif" && mime_content_type("img/" . $_SERVER['HTTP_FILE_NAME']) != "image/png") || ($path_parts['extension'] != "jpg" && $path_parts['extension'] != "gif" && $path_parts['extension'] != "png")) {
		unlink("img/" . $_SERVER['HTTP_FILE_NAME']);
		$json['error_msg'] = "Invalid file type!";
	} else if ($filesize > 1000000) {
		/* Check file size */
		unlink("img/" . $_SERVER['HTTP_FILE_NAME']);
		$json['error_msg'] = "File size is too large!";
	} else {
		// Upload success
		
		// Check duplicate	
	    if (file_exists("img/" . $_SERVER['HTTP_FILE_NAME'])) {
		    $sql = sprintf("DELETE FROM PHOTO WHERE filename = '%s'", mysql_real_escape_string($_SERVER['HTTP_FILE_NAME']));
			mysql_query($sql, $link);
	    }
		
		$sql = sprintf("INSERT INTO PHOTO (filename, size, upload_time, description, pathname) VALUES ('%s', '%s', NOW(), '', 'img/thumbnail/%s')", mysql_real_escape_string($_SERVER['HTTP_FILE_NAME']), mysql_real_escape_string($filesize), mysql_real_escape_string($_SERVER['HTTP_FILE_NAME']));
		mysql_query($sql, $link);
		$thumbnail = new Imagick("img/" . $_SERVER['HTTP_FILE_NAME']);
		$thumbnail->thumbnailImage(100, 0);
		$thumbnail->writeImage("img/thumbnail/" . $_SERVER['HTTP_FILE_NAME']); 
		$thumbnail->clear();
		$thumbnail->destroy();
	}
	
	echo json_encode($json);
	
?>