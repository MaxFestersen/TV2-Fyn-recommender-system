<?php
include '../../config/database.php';
$deviceID=$_POST['deviceID'];
$sessionID=$_POST['sessionID'];
$sql = "INSERT INTO `device_session`(`deviceID`, `sessionID`)
VALUES ('{$deviceID}', '{$sessionID}');";
if ($conn->query($sql) === TRUE) {
  echo "New record created successfully";
  } else {
    echo "Error: " . $sql . "<br>" . $conn->error;
  }
  $conn->close();
?>
