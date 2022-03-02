<?php
// Connect to database
$servername = 'db';
$username = 'recommender';
$password = rtrim(file_get_contents('/run/secrets/db_pass'));
$db = 'tv2fyn';

$conn = new mysqli($servername, $username, $password, $db);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}
?>

