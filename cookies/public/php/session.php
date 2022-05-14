<?php
header("Access-Control-Allow-Origin: *"); // change * to http://tv2fyn.dk
header('Content-type: text/plain; charset=utf-8'); // Set charset to utf-8
include(dirname(__DIR__).'../../config/database.php');

// PREPARE
$stmt = $conn -> prepare("INSERT INTO `session`(`deviceID`, `sessionID`) VALUES (?, ?)");
$stmt -> bind_param("ss", $deviceID, $sessionID);

// SET VALUES
$deviceID = filter_var($_POST['deviceID'], FILTER_SANITIZE_STRING);
$sessionID = filter_var($_POST['sessionID'], FILTER_SANITIZE_STRING);

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

