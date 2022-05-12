<?php
header("Access-Control-Allow-Origin: *"); // change * to http://tv2fyn.dk
header('Content-type: text/plain; charset=utf-8'); // Set charset to utf-8
include(dirname(__DIR__).'../../config/database.php');

// PREPARE
$stmt = $conn -> prepare("INSERT INTO `sessionInfo`(`sessionID`, `date`, `elapsed`, `articleID`, `scrollY`) VALUES (?, ?, ?, ?, ?)
ON DUPLICATE KEY UPDATE
`elapsed`= ADDTIME(VALUES(`elapsed`), `elapsed`), `scrollY`= GREATEST(VALUES(`scrollY`), `scrollY`);");
$stmt -> bind_param("ssssi", $sessionID, $date, $elapsed, $articleID, $scrollY);

// SET VALUES
$sessionID = filter_var($_POST['sessionID'], FILTER_SANITIZE_STRING);
$date = date('Y-m-d H:i:s');
$elapsed = filter_var(date('H:i:s', $_POST['elapsed']), FILTER_SANITIZE_STRING);
$articleID = filter_var($_POST['articleID'], FILTER_SANITIZE_STRING);
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

