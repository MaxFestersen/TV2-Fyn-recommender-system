<?php
header("Access-Control-Allow-Origin: *"); // change * to http://tv2fyn.dk
header('Content-type: text/plain; charset=utf-8'); // Set charset to utf-8
include(dirname(__DIR__).'../../config/database.php');

// PREPARE
$stmt = $conn -> prepare("INSERT INTO `sessionInfo`(`sessionID`, `date`, `elapsed`, `articleID`, `scrollY`, `lat`, `lon`) VALUES (?, ?, ?, ?, ?, ?, ?)");
$stmt -> bind_param("ssssidd", $sessionID, $date, $elapsed, $articleID, $scrollY, $lat, $lon);

// SET VALUES
$sessionID=$_POST['sessionID'];
$date=$_POST['date'];
$elapsed=$_POST['elapsed'];
$articleID=$_POST['articleID'];
$scrollY=$_POST['scrollY'];
$lat=str_replace(',', '.', $_POST['lat']);
$lon=str_replace(',', '.', $_POST['lon']);

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

