<?php
// Connect to database
require 'vendor/autoload.php';
$dotenv = Dotenv\Dotenv::createImmutable('/run/secrets/');
$dotenv->safeLoad();

$servername = $_ENV['MYSQL_HOST'];
$username = $_ENV['MYSQL_USER'];
$password = $_ENV['MYSQL_PASSWORD'];
$db = $_ENV['MYSQL_DATABASE'];

$conn = new mysqli($servername, $username, $password, $db);

// Check connection
if ($conn->connect_error) {
   die("Connection failed: " . $conn->connect_error);
}
?>

