-- phpMyAdmin SQL Dump
-- version 4.9.0.1
-- https://www.phpmyadmin.net/
--
-- Vært: 127.0.0.1
-- Genereringstid: 04. 02 2022 kl. 15:59:13
-- Serverversion: 10.4.6-MariaDB
-- PHP-version: 7.3.8

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";

--
-- Database: `tv2rs`
--

-- --------------------------------------------------------

--
-- Struktur-dump for tabellen `device`
--

CREATE TABLE `device` (
  `id` varchar(255) COLLATE utf8_danish_ci NOT NULL,
  `device` varchar(255) COLLATE utf8_danish_ci NOT NULL,
  `end` date NOT NULL,
  `screen_width` int(11) NOT NULL,
  `screen_height` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_danish_ci;

--
-- Begrænsninger for dumpede tabeller
--

--
-- Indeks for tabel `device`
--
ALTER TABLE `device`
  ADD PRIMARY KEY (`id`);
COMMIT;
