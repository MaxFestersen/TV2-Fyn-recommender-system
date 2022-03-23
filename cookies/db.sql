CREATE DATABASE IF NOT EXISTS tv2fyn;

CREATE TABLE IF NOT EXISTS tv2fyn.device(
deviceID VARCHAR(255) NOT NULL,
firstVisit DATE,
screenWidth INT(10),
screenHeight INT(10),
deviceOS VARCHAR(255) NOT NULL,
deviceVendor VARCHAR(255) NOT NULL,
PRIMARY KEY (deviceID)
);

CREATE TABLE IF NOT EXISTS tv2fyn.session(
deviceID VARCHAR(255) NOT NULL,
sessionID VARCHAR(255) NOT NULL,
PRIMARY KEY (sessionID),
FOREIGN KEY (deviceID) REFERENCES device(deviceID)
ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tv2fyn.sessionInfo(
sessionID varchar(255) NOT NULL,
date DATETIME,
elapsed TIME,
articleID VARCHAR(255) NOT NULL,
scrollY	INT(3),
lat FLOAT(6,3),
lon FLOAT(6,3),
PRIMARY KEY (sessionID, articleID),
FOREIGN KEY (sessionID) REFERENCES session(sessionID)
ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tv2fyn.articleLength(
articleID VARCHAR(255) NOT NULL,
length INT,
PRIMARY KEY (articleID),
FOREIGN KEY (articleID) REFERENCES sessionInfo(articleID)
);

INSERT INTO tv2fyn.articleLength(articleID, length) VALUES('placeholder', 123);
