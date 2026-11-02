-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: localhost    Database: alaga_db
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `animals`
--

DROP TABLE IF EXISTS `animals`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `animals` (
  `animal_id` int NOT NULL AUTO_INCREMENT,
  `animal_tag` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `animal_name` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `species` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `breed` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `sex` varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `birth_date` date DEFAULT NULL,
  `weight` decimal(10,2) DEFAULT NULL,
  `status` varchar(30) COLLATE utf8mb4_general_ci DEFAULT 'Active',
  `notes` text COLLATE utf8mb4_general_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `tag_number` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`animal_id`),
  UNIQUE KEY `animal_tag` (`animal_tag`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `animals`
--

LOCK TABLES `animals` WRITE;
/*!40000 ALTER TABLE `animals` DISABLE KEYS */;
INSERT INTO `animals` VALUES (1,NULL,'Stacey','dog','Husky','Male','2007-05-17',25.00,'Active',NULL,'2026-10-15 13:13:32','1'),(2,NULL,'Milo','dog','Husky','Female','2007-02-02',20.00,'Inactive',NULL,'2026-10-15 14:17:42','2');
/*!40000 ALTER TABLE `animals` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `breeding_records`
--

DROP TABLE IF EXISTS `breeding_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `breeding_records` (
  `breeding_id` int NOT NULL AUTO_INCREMENT,
  `animal_id` int NOT NULL,
  `mate_id` int DEFAULT NULL,
  `breeding_date` date NOT NULL,
  `expected_birth_date` date DEFAULT NULL,
  `status` varchar(50) COLLATE utf8mb4_general_ci DEFAULT 'Pending',
  `notes` text COLLATE utf8mb4_general_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `mate_tag_number` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `actual_birth_date` date DEFAULT NULL,
  `offspring_count` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`breeding_id`),
  KEY `animal_id` (`animal_id`),
  KEY `mate_id` (`mate_id`),
  CONSTRAINT `breeding_records_ibfk_1` FOREIGN KEY (`animal_id`) REFERENCES `animals` (`animal_id`) ON DELETE CASCADE,
  CONSTRAINT `breeding_records_ibfk_2` FOREIGN KEY (`mate_id`) REFERENCES `animals` (`animal_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `breeding_records`
--

LOCK TABLES `breeding_records` WRITE;
/*!40000 ALTER TABLE `breeding_records` DISABLE KEYS */;
INSERT INTO `breeding_records` VALUES (1,1,NULL,'2009-03-01','2009-05-17','Pending',NULL,'2026-10-15 14:18:37','2','2010-05-17',2);
/*!40000 ALTER TABLE `breeding_records` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `feeding_records`
--

DROP TABLE IF EXISTS `feeding_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `feeding_records` (
  `feeding_id` int NOT NULL AUTO_INCREMENT,
  `animal_id` int NOT NULL,
  `feed_type` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `quantity` decimal(10,2) NOT NULL,
  `feeding_date` date NOT NULL,
  `notes` text COLLATE utf8mb4_general_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `unit` varchar(30) COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'kg',
  `feeding_time` time DEFAULT NULL,
  PRIMARY KEY (`feeding_id`),
  KEY `animal_id` (`animal_id`),
  CONSTRAINT `feeding_records_ibfk_1` FOREIGN KEY (`animal_id`) REFERENCES `animals` (`animal_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `feeding_records`
--

LOCK TABLES `feeding_records` WRITE;
/*!40000 ALTER TABLE `feeding_records` DISABLE KEYS */;
INSERT INTO `feeding_records` VALUES (3,2,'Whiskas',1.00,'2016-01-29','None','2026-10-30 16:47:27','1kg','01:26:10');
/*!40000 ALTER TABLE `feeding_records` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `health_records`
--

DROP TABLE IF EXISTS `health_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `health_records` (
  `health_id` int NOT NULL AUTO_INCREMENT,
  `animal_id` int NOT NULL,
  `record_date` date NOT NULL,
  `condition_name` varchar(150) COLLATE utf8mb4_general_ci NOT NULL,
  `treatment` text COLLATE utf8mb4_general_ci,
  `veterinarian` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `notes` text COLLATE utf8mb4_general_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`health_id`),
  KEY `animal_id` (`animal_id`),
  CONSTRAINT `health_records_ibfk_1` FOREIGN KEY (`animal_id`) REFERENCES `animals` (`animal_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `health_records`
--

LOCK TABLES `health_records` WRITE;
/*!40000 ALTER TABLE `health_records` DISABLE KEYS */;
INSERT INTO `health_records` VALUES (1,1,'2007-02-02','Recovering','none','edmar','None','2026-10-15 14:16:57'),(2,1,'2007-02-02','Healthy','none','edmar','none','2026-10-15 14:36:12');
/*!40000 ALTER TABLE `health_records` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `password_hash` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `full_name` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `role` varchar(50) COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'User',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'admin','2aca2428e1d5cde08ec0f70b904e9e6d$0ac913589867ee499de2d5af9fa23b4ccc3316c42e838ca51fff34542484e618','Administrator','System Administrator','2026-10-15 12:53:35');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `vaccinations`
--

DROP TABLE IF EXISTS `vaccinations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `vaccinations` (
  `vaccination_id` int NOT NULL AUTO_INCREMENT,
  `animal_id` int NOT NULL,
  `vaccine_name` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `vaccination_date` date NOT NULL,
  `next_due_date` date DEFAULT NULL,
  `veterinarian` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `notes` text COLLATE utf8mb4_general_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`vaccination_id`),
  KEY `animal_id` (`animal_id`),
  CONSTRAINT `vaccinations_ibfk_1` FOREIGN KEY (`animal_id`) REFERENCES `animals` (`animal_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `vaccinations`
--

LOCK TABLES `vaccinations` WRITE;
/*!40000 ALTER TABLE `vaccinations` DISABLE KEYS */;
INSERT INTO `vaccinations` VALUES (3,1,'corona','2007-02-02','2009-02-02',NULL,NULL,'2026-10-15 14:15:17');
/*!40000 ALTER TABLE `vaccinations` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-11-02 17:51:31
