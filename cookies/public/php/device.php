<?php
include '../../config/database.php';

// PREPARE
$stmt = $conn -> prepare("INSERT INTO `device` (`deviceID`, `firstVisit`, `screenWidth`, `screenHeight`, `deviceOS`, `deviceVendor`) VALUES (?, ?, ?, ?, ?, ?)");
$stmt -> bind_param("ssiiss", $deviceID, $firstVisit, $screenWidth, $screenHeight, $deviceOS, $deviceVendor);

// EXECUTE
$deviceID=$_POST['deviceID'];
$firstVisit=$_POST['firstVisit'];
$screenWidth=$_POST['screenWidth'];
$screenHeight=$_POST['screenHeight'];
$deviceOS=$_POST['deviceOS'];
$deviceVendor=$_POST['deviceVendor'];

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