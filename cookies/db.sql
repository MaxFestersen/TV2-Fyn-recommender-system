CREATE DATABASE IF NOT EXISTS tv2fyn;

CREATE TABLE IF NOT EXISTS tv2fyn.device(
deviceID varchar(255) NOT NULL,
firstVisit DATE,
screenWidth int(10),
screenHeight int(10),
PRIMARY KEY (deviceID)
);

CREATE TABLE IF NOT EXISTS tv2fyn.session(
deviceID varchar(255) NOT NULL,
date DATE,
elapsed time,
articleID varchar(255) NOT NULL,
scrollY	varchar(255),
lat FLOAT(6,3),
lon FLOAT(6,3),
PRIMARY KEY (articleID),
FOREIGN KEY (deviceID) REFERENCES device(deviceID)
);

