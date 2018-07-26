<?php
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "blackdoor";

$catchCmd = $_POST['cmdCatch'];
print $catchCmd;

// Connect
$mysqli = new mysqli("localhost", "root", "", "blackdoor");

/* check connection */
if (mysqli_connect_errno()) {
    printf("Connect failed: %s\n", mysqli_connect_error());
    exit();
}

// Extract Row Count
if ($result = $mysqli->query("SELECT ID, CMD FROM cmdhist ORDER BY ID")) {

    $row_cnt = $result->num_rows;

    $row_cnt = $row_cnt + 1;

    $result->close();
}

// Insert New Row
$sql = "INSERT INTO cmdhist (ID, CMD)
VALUES (" . $row_cnt . ", '" . $catchCmd . "')";
if ($mysqli->query($sql) === TRUE) {
    echo "New record created successfully";
} else {
    echo "Error: " . $sql . "<br>" . $mysqli->error;
}

?>
