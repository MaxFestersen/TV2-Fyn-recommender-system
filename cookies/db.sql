CREATE DATABASE IF NOT EXISTS tv2fyn;

CREATE TABLE IF NOT EXISTS tv2fyn.device(
deviceID varchar(255) NOT NULL,
firstVisit DATE,
screenWidth int(10),
screenHeight int(10),
PRIMARY KEY (deviceID)
);

CREATE TABLE IF NOT EXISTS tv2fyn.device_session(
deviceID varchar(255) NOT NULL,
sessionID varchar(255) NOT NULL,
PRIMARY KEY (sessionID),
FOREIGN KEY (deviceID) REFERENCES device(deviceID)
);

CREATE TABLE IF NOT EXISTS tv2fyn.session(
sessionID varchar(255) NOT NULL,
date DATE,
elapsed time,
articleID varchar(255) NOT NULL,
scrollY	float(5,3),
lat FLOAT(6,3),
lon FLOAT(6,3),
PRIMARY KEY (sessionID, articleID),
FOREIGN KEY (sessionID) REFERENCES device_session(sessionID)
);
