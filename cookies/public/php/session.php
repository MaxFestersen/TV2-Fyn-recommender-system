<?php
include '../../config/database.php';
$sessionID=$_POST['sessionID'];
$date=$_POST['date'];
$elapsed=$_POST['elapsed'];
$articleID=$_POST['articleID'];
$scrollY=$_POST['scrollY'];
$lat=str_replace(',', '.', $_POST['lat']);
$lon=str_replace(',', '.', $_POST['lon']);
$sql = "INSERT INTO `session`(`sessionID`, `date`, `elapsed`, `articleID`, `scrollY`, `lat`, `lon`)
VALUES ('{$sessionID}', '{$date}', '{$elapsed}', '{$articleID}', '{$scrollY}', '{$lat}', '{$lon}');";
if ($conn->query($sql) === TRUE) {
  echo "New record created successfully";
  } else {
    echo "Error: " . $sql . "<br>" . $conn->error;
  }
  $conn->close();
?>