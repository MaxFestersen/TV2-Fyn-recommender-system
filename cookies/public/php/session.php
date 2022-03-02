<?php
header("Access-Control-Allow-Origin: *"); // change * to http://tv2fyn.dk
include(dirname(__DIR__).'../../config/database.php');

// PREPARE
$stmt = $conn -> prepare("INSERT INTO `session`(`deviceID`, `sessionID`) VALUES (?, ?)");
$stmt -> bind_param("ss", $deviceID, $sessionID);

// SET VALUES
$deviceID=$_POST['deviceID'];
$sessionID=$_POST['sessionID'];

// EXECUTE & PRINT RESULT
if ($stmt->execute() === TRUE) {
	echo "New record created successfully";
} else {
	//echo "Error: " . $sql . "<br>" . $conn->error;
	echo "Error.<br>" . $stmt->error;
}

//CLOSE CONNECTIONS
$stmt->close();
$conn->close();
?>

