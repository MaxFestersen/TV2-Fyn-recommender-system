<?php
header("Access-Control-Allow-Origin: *"); // change * to http://tv2fyn.dk
header('Content-type: text/plain; charset=utf-8'); // Set charset to utf-8
include(dirname(__DIR__).'../../config/database.php');

// PREPARE
$stmt = $conn -> prepare("INSERT INTO `device` (`deviceID`, `firstVisit`, `screenWidth`, `screenHeight`, `deviceOS`, `deviceVendor`) VALUES (?, ?, ?, ?, ?, ?)");
$stmt -> bind_param("ssiiss", $deviceID, $firstVisit, $screenWidth, $screenHeight, $deviceOS, $deviceVendor);

// EXECUTE
$deviceID=$_POST['deviceID'];
$firstVisit= date('Y-m-d');
$screenWidth=$_POST['screenWidth'];
$screenHeight=$_POST['screenHeight'];
$deviceOS=$_POST['deviceOS'];
$deviceVendor=$_POST['deviceVendor'];

// EXECUTE & PRINT RESULT
if ($stmt->execute() === TRUE) {
	echo "New record created successfully";
} else {
	echo "Error.<br>" . $stmt->error;
}

//CLOSE CONNECTIONS
$stmt->close();
$conn->close();
?>
