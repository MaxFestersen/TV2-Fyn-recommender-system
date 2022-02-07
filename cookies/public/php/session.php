<?php
include '../../config/database.php';
$deviceID=$_POST['deviceID'];
$date=$_POST['date'];
$elapsed=$_POST['elapsed'];
$articleID=$_POST['articleID'];
$scrollY=$_POST['scrollY'];
$sql = "INSERT INTO `session`(`deviceID`, `date`, `elapsed`, `articleID`, `scrollY`)
VALUES ('{$deviceID}', '{$date}', '{$elapsed}', '{$articleID}', '{$scrollY}')
ON DUPLICATE KEY UPDATE
`deviceID`='{$deviceID}', `date`='{$date}', `elapsed`='{$elapsed}', `articleID`='{$articleID}', `scrollY`='{$scrollY}';";
if ($conn->query($sql) === TRUE) {
  echo "New record created successfully";
  } else {
    echo "Error: " . $sql . "<br>" . $conn->error;
  }
  $conn->close();
?>