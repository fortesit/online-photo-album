use CGI;

$q = CGI -> new;
print $q->redirect("index.cgi");