<?php
header("Access-Control-Allow-Origin: *"); // change * to http://tv2fyn.dk
header('Content-type: text/plain; charset=utf-8'); // Set charset to utf-8
include(dirname(__DIR__).'../../config/database.php');

// SET VALUES
$sessionID=$_POST['sessionID'];
$date= date('Y-m-d H:i:s');
$elapsed=date('H:i:s', $_POST['elapsed']);
$articleID=$_POST['articleID'];
$scrollY=$_POST['scrollY'];

// CHECK IF EXISTS
// CHECK IF EXISTS: Connection and bind params
$existsCheck = $conn -> prepare("SELECT COUNT(sessionID) FROM `sessionInfo` WHERE sessionID=? AND articleID=?");
//$existsCheck = $conn -> prepare("SELECT sessionID, articleID FROM `sessionInfo` WHERE sessionID=? AND articleID=? LIMIT 1");
$existsCheck -> bind_param("ss", $sessionID, $articleID);

// CHECK IF EXISTS: SET VALUES
$existsCheck->execute();

// GET RESULTS
$result = $existsCheck->get_result();

// LOOP RESULTS (allthough it would seem unecesarry, a simple check seems to fail randomly, but that is surely another fault)
$row = $result->fetch_assoc();	//echo $row["COUNT(sessionID)"];
$existsCheck->close();
if($row["COUNT(sessionID)"]==0){
	// PREPARE
	$stmt = $conn -> prepare("INSERT INTO `sessionInfo`(`sessionID`, `date`, `elapsed`, `articleID`, `scrollY`) VALUES (?, ?, ?, ?, ?)");
	$stmt -> bind_param("ssssi", $sessionID, $date, $elapsed, $articleID, $scrollY);
	
	// EXECUTE & PRINT RESULT
	if ($stmt->execute() === TRUE) {
		echo "New record created successfully";
	} else {
		//echo "Error: " . $sql . "<br>" . $conn->error;
		echo "Error.<br>" . $stmt->error;
	}
	$stmt->close();
}

//CLOSE CONNECTIONS
$conn->close();
?>

