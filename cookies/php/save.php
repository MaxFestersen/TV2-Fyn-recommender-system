<?php
include 'database.php';
$deviceID=$_POST['deviceID'];
$firstVisit=$_POST['firstVisit'];
$screenWidth=$_POST['screenWidth'];
$screenHeight=$_POST['screenHeight'];
$sql = "INSERT INTO device(deviceID, firstVisit, screenWidth, screenHeight)
VALUES ('$deviceID', '$firstVisit', '$screenWidth', '$screenHeight')";
$conn->query($sql);
if ($conn->query($sql) === TRUE) {
  echo "New record created successfully";
  } else {
    echo "Error: " . $sql . "<br>" . $conn->error;
  }
  $conn->close();
?>