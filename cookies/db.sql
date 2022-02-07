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
scrollY	varchar(255),
PRIMARY KEY (articleID),
FOREIGN KEY (sessionID) REFERENCES device_session(sessionID)
);

