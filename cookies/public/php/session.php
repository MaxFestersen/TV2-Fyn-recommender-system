<?php
include '../../config/database.php';
$sessionID=$_POST['sessionID'];
$date=$_POST['date'];
$elapsed=$_POST['elapsed'];
$articleID=$_POST['articleID'];
$scrollY=$_POST['scrollY'];
$sql = "INSERT INTO `session`(`sessionID`, `date`, `elapsed`, `articleID`, `scrollY`)
VALUES ('{$sessionID}', '{$date}', '{$elapsed}', '{$articleID}', '{$scrollY}')
ON DUPLICATE KEY UPDATE
`sessionID`='{$sessionID}', `date`='{$date}', `elapsed`='{$elapsed}', `articleID`='{$articleID}', `scrollY`='{$scrollY}';";
if ($conn->query($sql) === TRUE) {
  echo "New record created successfully";
  } else {
    echo "Error: " . $sql . "<br>" . $conn->error;
  }
  $conn->close();
?>