CREATE DATABASE IF NOT EXISTS tv2fyn;

CREATE TABLE IF NOT EXISTS tv2fyn.device(
deviceID varchar(255) NOT NULL,
firstVisit DATE,
screenWidth int(10),
screenHeight int(10),
deviceOS varchar(255) NOT NULL,
deviceVendor varchar(255) NOT NULL,
PRIMARY KEY (deviceID)
);

CREATE TABLE IF NOT EXISTS tv2fyn.session(
deviceID varchar(255) NOT NULL,
sessionID varchar(255) NOT NULL,
PRIMARY KEY (sessionID),
FOREIGN KEY (deviceID) REFERENCES device(deviceID)
ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tv2fyn.sessionInfo(
sessionID varchar(255) NOT NULL,
date DATETIME,
elapsed time,
articleID varchar(255) NOT NULL,
scrollY	int(3),
lat FLOAT(6,3),
lon FLOAT(6,3),
PRIMARY KEY (sessionID, articleID),
FOREIGN KEY (sessionID) REFERENCES session(sessionID)
ON DELETE CASCADE
);
