<?php
header("Access-Control-Allow-Origin: *"); // change * to http://tv2fyn.dk
include(dirname(__DIR__).'../../config/database.php');

// PREPARE
$stmt = $conn -> prepare("INSERT INTO `sessionInfo`(`sessionID`, `elapsed`, `articleID`, `scrollY`) VALUES (?, ?, ?, ?)
ON DUPLICATE KEY UPDATE
`elapsed`= ADDTIME(VALUES(`elapsed`), `elapsed`), `scrollY`= GREATEST(VALUES(`scrollY`), `scrollY`);");
$stmt -> bind_param("sssi", $sessionID, $elapsed, $articleID, $scrollY);

// SET VALUES
$sessionID=$_POST['sessionID'];
$elapsed=$_POST['elapsed'];
$articleID=$_POST['articleID'];
$scrollY=$_POST['scrollY'];

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

