<?php
$path = $_SERVER['DOCUMENT_ROOT'];
$path .= "/config/tv2RSdatabase.php";
include $path;
$deviceID=$_POST['deviceID'];
$firstVisit=$_POST['firstVisit'];
$screenWidth=$_POST['screenWidth'];
$screenHeight=$_POST['screenHeight'];
$sql = "INSERT INTO `device`(`deviceID`, `firstVisit`, `screenWidth`, `screenHeight`)
VALUES ('{$deviceID}', '{$firstVisit}', '{$screenWidth}', '{$screenHeight}');";
if ($conn->query($sql) === TRUE) {
  echo "New record created successfully";
  } else {
    echo "Error: " . $sql . "<br>" . $conn->error;
  }
  $conn->close();
?>