<?php
include '../../config/database.php';
$deviceID=$_POST['deviceID'];
$date=$_POST['date'];
$elapsed=$_POST['elapsed'];
$articleID=$_POST['articleID'];
$scrollY=$_POST['scrollY'];
$lat=str_replace(',', '.', $_POST['lat']);
$lon=str_replace(',', '.', $_POST['lon']);

$sql = "INSERT INTO `session`(`deviceID`, `date`, `elapsed`, `articleID`, `scrollY`, `lat`, `lon`)
VALUES ('{$deviceID}', '{$date}', '{$elapsed}', '{$articleID}', '{$scrollY}', '{$lat}', '{$lon}')
ON DUPLICATE KEY UPDATE
`deviceID`='{$deviceID}', `date`='{$date}', `elapsed`='{$elapsed}', `articleID`='{$articleID}', `scrollY`='{$scrollY}', `lat`='{$lat}', `lon`='{$lon}';";
if ($conn->query($sql) === TRUE) {
  echo "New record created successfully";
  } else {
    echo "Error: " . $sql . "<br>" . $conn->error;
  }
  $conn->close();
?>