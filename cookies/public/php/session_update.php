<?php
include '../../config/database.php';

// PREPARE
$stmt = $conn -> prepare("INSERT INTO `session`(`sessionID`, `elapsed`, `articleID`, `scrollY`) VALUES (?, ?, ?, ?)
ON DUPLICATE KEY UPDATE
`elapsed`= ADDTIME(VALUES(`elapsed`), `elapsed`), `scrollY`= GREATEST(VALUES(`scrollY`), `scrollY`);");
$stmt -> bind_param("sssi", $sessionID, $elapsed, $articleID, $scrollY);

// SET VALUES
$sessionID=$_POST['sessionID'];
//$date=$_POST['date'];
$elapsed=$_POST['elapsed'];
$articleID=$_POST['articleID'];
$scrollY=$_POST['scrollY'];
//$lat=str_replace(',', '.', $_POST['lat']);
//$lon=str_replace(',', '.', $_POST['lon']);

// EXECUTE & PRINT RESULT
if ($stmt->execute() === TRUE) {
	echo "New record created successfully";
} else {
	//echo "Error: " . $sql . "<br>" . $conn->error;
	echo "Error.<br>" . $stmt->error;
}
$TEXT = "'hej'; drop database'";
//CLOSE CONNECTIONS
$stmt->close();
$conn->close();
?>