-- MySQL dump 10.13  Distrib 8.0.45, for Linux (x86_64)
--
-- Host: localhost    Database: leave_system
-- ------------------------------------------------------
-- Server version	8.0.45-0ubuntu0.24.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `leaves`
--

DROP TABLE IF EXISTS `leaves`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `leaves` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '请假ID',
  `user_id` int NOT NULL COMMENT '申请人用户ID',
  `student_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '学生姓名（冗余存储）',
  `leave_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '请假类型: 病假/事假/公假等',
  `in_class` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '是否在班: yes/no',
  `destination` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '请假去向',
  `detail_address` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '详细地址',
  `start_time` datetime NOT NULL COMMENT '请假开始时间',
  `end_time` datetime NOT NULL COMMENT '请假结束时间',
  `reason` text COLLATE utf8mb4_unicode_ci COMMENT '请假理由',
  `emergency_contact` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '紧急联系人',
  `emergency_phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '紧急联系电话',
  `attachment` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '附件文件路径',
  `status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'pending' COMMENT 'pending(待审核), approved(已批准), rejected(已拒绝), invalidated(已销假)',
  `remarks` text COLLATE utf8mb4_unicode_ci COMMENT '审批备注',
  `approver_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '审批人名字（由申请人填写）',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '申请提交时间',
  `approved_at` datetime DEFAULT NULL COMMENT '审批完成时间',
  `approved_by` int DEFAULT NULL COMMENT '审批人ID',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_status` (`status`),
  KEY `idx_approved_by` (`approved_by`),
  KEY `idx_start_time` (`start_time`),
  KEY `idx_created_at` (`created_at`),
  CONSTRAINT `leaves_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `leaves_ibfk_2` FOREIGN KEY (`approved_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=60 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='请假申请表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `leaves`
--

LOCK TABLES `leaves` WRITE;
/*!40000 ALTER TABLE `leaves` DISABLE KEYS */;
INSERT INTO `leaves` VALUES (1,2,NULL,'节假日及寒暑假请假',NULL,'离校不离市','广东省-广州市-白云区-广东警官学院','2026-01-17 15:41:00','2026-01-18 15:41:00','外出','麦恺晖','13414981310',NULL,'approved',NULL,'刘明月','2026-01-17 15:42:15','2026-01-17 16:07:07',1),(2,11,NULL,'其他',NULL,'离校不离市','广东省-广州市-白云区-嘉禾望岗','2026-01-18 10:52:00','2026-01-18 21:52:00','周末出校','陈咏娴','15989971934',NULL,'approved',NULL,'刘明月','2026-01-17 15:52:51','2026-01-17 16:07:09',1),(3,10,NULL,'节假日及寒暑假请假',NULL,'离校不离市','','2025-12-31 12:30:00','2026-01-03 17:00:00','元旦','','',NULL,'invalidated',NULL,'管理员','2026-01-17 15:56:16',NULL,NULL),(4,10,NULL,'节假日及寒暑假请假',NULL,'离校不离市','','2025-12-19 17:00:00','2025-12-21 17:00:00','夜假','','',NULL,'invalidated',NULL,'管理员','2026-01-17 15:56:16',NULL,NULL),(5,10,NULL,'其它',NULL,'离校不离市','','2025-11-29 09:00:00','2025-11-29 22:30:00','周末离校','','',NULL,'invalidated',NULL,'管理员','2026-01-17 15:56:16',NULL,NULL),(6,10,NULL,'其它',NULL,'离校不离市','','2025-11-28 17:00:00','2025-11-28 22:30:00','周末离校','','',NULL,'invalidated',NULL,'管理员','2026-01-17 15:56:16',NULL,NULL),(7,10,NULL,'节假日及寒暑假请假',NULL,'离校不离市','','2025-11-22 14:00:00','2025-11-27 19:00:00','放假','','',NULL,'invalidated',NULL,'管理员','2026-01-17 15:56:16',NULL,NULL),(8,10,NULL,'其它',NULL,'离校不离市','','2025-11-01 08:00:00','2025-11-01 22:30:00','周末离校','','',NULL,'invalidated',NULL,'管理员','2026-01-17 15:56:16',NULL,NULL),(9,10,NULL,'其它',NULL,'离校不离市','','2025-11-02 08:00:00','2025-11-02 18:00:00','周末离校','','',NULL,'invalidated',NULL,'管理员','2026-01-17 15:56:16',NULL,NULL),(10,10,NULL,'其它',NULL,'离校不离市','','2025-10-31 17:00:00','2025-10-31 22:30:00','周末离校','','',NULL,'invalidated',NULL,'管理员','2026-01-17 15:56:16',NULL,NULL),(11,10,NULL,'其它',NULL,'离校不离市','','2025-10-24 17:00:00','2025-10-24 22:30:00','周末离校','','',NULL,'invalidated',NULL,'管理员','2026-01-17 15:56:16',NULL,NULL),(12,10,NULL,'其它',NULL,'离校不离市','','2025-10-25 08:00:00','2025-10-25 22:30:00','周末离校','','',NULL,'invalidated',NULL,'管理员','2026-01-17 15:56:16',NULL,NULL),(13,12,NULL,'其他',NULL,'离校不离市','广东省-广州市-白云区-白云区','2026-01-17 16:07:00','2026-01-17 19:07:00','周末外出','王廖聪','13723473486',NULL,'approved',NULL,'刘明月','2026-01-17 16:07:38','2026-01-17 16:07:51',1),(14,14,NULL,'病假',NULL,'离校不离市','广东省-广州市-白云区-后门','2026-01-17 16:33:00','2026-01-18 22:33:00','看病','陈子兴','13686265802',NULL,'approved',NULL,'耿武奎','2026-01-17 16:34:48','2026-01-17 16:37:15',1),(15,15,NULL,'节假日及寒暑假请假',NULL,'离校不离市','广东省-广州市-白云区-hh','2026-01-17 16:50:00','2026-01-17 21:50:00','ss','s','1',NULL,'approved',NULL,'刘明月','2026-01-17 16:51:05','2026-01-17 16:51:10',1),(16,16,NULL,'节假日及寒暑假请假',NULL,'不离校','广东省-佛山市-禅城区-1','2026-01-17 16:58:00','2026-01-17 17:00:00','1','1','1',NULL,'invalidated',NULL,'1','2026-01-17 16:58:25','2026-01-17 16:58:49',1),(17,18,NULL,'节假日及寒暑假请假',NULL,'离校不离市','广东省-广州市-白云区-广东警官学院','2026-01-18 07:00:00','2026-01-18 18:00:00','恰饭','曾兆康','15626962305',NULL,'approved',NULL,'刘明月','2026-01-17 18:14:46','2026-01-17 18:15:05',1),(18,18,NULL,'节假日及寒暑假请假',NULL,'离校不离市','广东省-广州市-白云区-广东警官学院','2026-01-17 07:05:00','2026-01-17 22:28:00','恰饭','曾兆康','15626962385',NULL,'invalidated',NULL,'刘明月','2026-01-17 18:23:37','2026-01-17 18:23:41',1),(20,20,NULL,'节假日及寒暑假请假',NULL,'离校不离市','广东省-广州市-白云区-文盛庄路112号广东警官学院','2026-01-18 06:20:00','2026-01-18 22:30:00','周末外出','林光辉','13750411311',NULL,'approved',NULL,'刘明月','2026-01-18 00:21:36','2026-01-18 00:22:21',1),(21,23,NULL,'其他',NULL,'离校不离市','广东省-广州市-白云区-东平','2026-01-18 08:11:00','2026-01-18 17:12:00','外出','刘子慧','13532111209',NULL,'invalidated',NULL,'刘明月','2026-01-18 17:12:22','2026-01-18 17:13:47',1),(22,24,NULL,'节假日及寒暑假请假',NULL,'离校不离市','广东省-广州市-白云区-后门','2026-01-19 20:21:00','2026-01-29 20:21:00','无','刘均旭','13702996911',NULL,'approved',NULL,'陈子姓','2026-01-19 20:21:59','2026-01-19 20:26:43',1),(23,25,NULL,'其他',NULL,'离校不离市','福建省-泉州市-永春县-111','2026-01-19 20:24:00','2026-01-26 20:24:00','1','aa','aa',NULL,'approved',NULL,'耿武奎','2026-01-19 20:24:50','2026-01-19 20:26:41',1),(24,25,NULL,'其它',NULL,'离校不离市','','2026-01-16 17:00:00','2026-01-16 22:00:00','出去玩','','',NULL,'invalidated',NULL,'管理员','2026-01-19 22:25:35',NULL,NULL),(25,25,NULL,'其它',NULL,'离校不离市','','2026-01-09 17:10:00','2026-01-09 22:22:00','出去玩','','',NULL,'invalidated',NULL,'管理员','2026-01-19 22:25:35',NULL,NULL),(26,25,NULL,'节假日及寒暑假请假',NULL,'离校不离市','','2025-12-31 13:59:00','2026-01-03 16:59:00','回家','','',NULL,'invalidated',NULL,'管理员','2026-01-19 22:25:35',NULL,NULL),(27,25,NULL,'其它',NULL,'离校不离市','','2025-12-28 07:45:00','2025-12-28 17:00:00','出去玩','','',NULL,'invalidated',NULL,'管理员','2026-01-19 22:25:35',NULL,NULL),(28,25,NULL,'其它',NULL,'离校不离市','','2025-12-26 17:11:00','2025-12-26 22:30:00','出去玩','','',NULL,'invalidated',NULL,'管理员','2026-01-19 22:25:35',NULL,NULL),(29,25,NULL,'其它',NULL,'离校不离市','','2025-12-21 07:08:00','2025-12-21 16:47:00','出去玩','','',NULL,'invalidated',NULL,'管理员','2026-01-19 22:25:35',NULL,NULL),(30,25,NULL,'其它',NULL,'离校不离市','','2025-12-20 07:30:00','2025-12-20 22:00:00','出去玩','','',NULL,'invalidated',NULL,'管理员','2026-01-19 22:25:35',NULL,NULL),(31,25,NULL,'其它',NULL,'离校不离市','','2025-12-19 17:00:00','2025-12-19 22:11:00','出去玩','','',NULL,'invalidated',NULL,'管理员','2026-01-19 22:25:35',NULL,NULL),(32,25,NULL,'其它',NULL,'离校不离市','','2025-12-12 16:50:00','2025-12-14 16:59:00','回家办事','','',NULL,'invalidated',NULL,'管理员','2026-01-19 22:25:35',NULL,NULL),(33,25,NULL,'其它',NULL,'离校不离市','','2025-10-12 07:13:00','2025-10-12 18:45:00','出去玩','','',NULL,'invalidated',NULL,'管理员','2026-01-19 22:25:35',NULL,NULL),(34,27,NULL,'节假日及寒暑假请假',NULL,'离校不离市','广东省-深圳市-宝安区-西乡街道','2026-01-18 12:17:00','2026-01-20 12:17:00','外出访友','张三','13530888920',NULL,'invalidated',NULL,'耿武奎','2026-01-20 12:18:50','2026-01-20 12:19:57',1),(35,28,NULL,'其他',NULL,'离校不离市','广东省-广州市-白云区-1','2026-01-21 14:45:00','2026-01-22 20:45:00','放假','c','1',NULL,'invalidated',NULL,'刘明月','2026-01-20 14:46:08','2026-01-20 14:46:34',1),(36,29,NULL,'事假',NULL,'离校不离市','广东省-广州市-白云区-广东警官学院','2026-03-05 14:00:00','2026-03-05 18:00:00','事假','邓肖凤','18128573832',NULL,'invalidated',NULL,'刘明月','2026-03-05 09:11:10','2026-03-05 09:11:25',1),(37,29,NULL,'节假日及寒暑假请假',NULL,'离校不离市','','2026-01-19 17:00:00','2026-03-03 19:00:00','寒假','','',NULL,'invalidated',NULL,'管理员','2026-03-05 09:16:20',NULL,NULL),(38,29,NULL,'节假日及寒暑假请假',NULL,'离校不离市','','2026-01-17 08:00:00','2026-01-17 22:30:00','周末外出','','',NULL,'invalidated',NULL,'管理员','2026-03-05 09:16:20',NULL,NULL),(39,29,NULL,'节假日及寒暑假请假',NULL,'离校不离市','','2026-01-16 17:00:00','2026-01-16 22:30:00','周末外出','','',NULL,'invalidated',NULL,'管理员','2026-03-05 09:16:20',NULL,NULL),(40,29,NULL,'节假日及寒暑假请假',NULL,'离校不离市','','2026-01-11 08:00:00','2026-01-11 17:00:00','周末外出','','',NULL,'invalidated',NULL,'管理员','2026-03-05 09:16:20',NULL,NULL),(41,29,NULL,'节假日及寒暑假请假',NULL,'离校不离市','','2026-01-10 08:00:00','2026-01-10 23:00:00','周末外出','','',NULL,'invalidated',NULL,'管理员','2026-03-05 09:16:20',NULL,NULL),(42,29,NULL,'节假日及寒暑假请假',NULL,'离校不离市','','2026-01-09 17:00:00','2026-01-09 23:00:00','周末外出','','',NULL,'invalidated',NULL,'管理员','2026-03-05 09:16:20',NULL,NULL),(43,29,NULL,'节假日及寒暑假请假',NULL,'离校不离市','','2025-12-26 17:00:00','2025-12-28 17:00:00','夜假','','',NULL,'invalidated',NULL,'管理员','2026-03-05 09:16:20',NULL,NULL),(44,29,NULL,'节假日及寒暑假请假',NULL,'离校不离市','','2025-12-21 08:00:00','2025-12-21 17:00:00','周末外出','','',NULL,'invalidated',NULL,'管理员','2026-03-05 09:16:20',NULL,NULL),(45,29,NULL,'节假日及寒暑假请假',NULL,'离校不离市','','2025-12-20 08:00:00','2025-12-20 22:30:00','周末外出','','',NULL,'invalidated',NULL,'管理员','2026-03-05 09:16:20',NULL,NULL),(46,29,NULL,'节假日及寒暑假请假',NULL,'离校不离市','','2025-12-19 17:00:00','2025-12-19 22:30:00','周末外出','','',NULL,'invalidated',NULL,'管理员','2026-03-05 09:16:20',NULL,NULL),(47,29,NULL,'事假',NULL,'离校不离市','广东省-广州市-白云区-广东警官学院','2026-03-05 14:00:00','2026-03-05 18:00:00','事假','邓肖凤','18128573832',NULL,'invalidated',NULL,'刘明月','2026-03-05 09:19:26','2026-03-05 09:19:59',1),(48,29,NULL,'节假日及寒暑假请假',NULL,'离校不离市','广东省-广州市-白云区-广东警官学院','2026-03-10 16:00:00','2026-03-10 19:00:00','外出','邓肖凤','18128573832',NULL,'invalidated',NULL,'刘明月','2026-03-10 12:16:36','2026-03-10 12:19:43',1),(49,29,NULL,'事假',NULL,'离校不离市','广东省-广州市-白云区-广东警官学院','2026-03-10 16:00:00','2026-03-10 19:00:00','事假','邓肖凤','18128573832',NULL,'invalidated',NULL,'刘明月','2026-03-10 12:24:24','2026-03-10 12:25:23',1),(50,31,NULL,'节假日及寒暑假请假',NULL,'离校不离市','广东省-广州市-白云区-广警','2026-03-10 16:40:00','2026-03-10 19:40:00','外出','秦振翔','18928066081',NULL,'invalidated',NULL,'刘明月','2026-03-10 16:40:31','2026-03-10 16:40:52',1),(51,29,NULL,'事假',NULL,'离校不离市','广东省-广州市-白云区-广东警官学院','2026-03-12 14:00:00','2026-03-12 18:00:00','事假','邓肖凤','18128573832',NULL,'invalidated',NULL,'刘明月','2026-03-12 12:47:32','2026-03-12 12:49:02',1),(52,31,NULL,'节假日及寒暑假请假',NULL,'离校不离市','广东省-广州市-白云区-广警','2026-03-12 14:06:00','2026-03-12 18:06:00','外出','秦振翔','18928066081',NULL,'invalidated',NULL,'刘明月','2026-03-12 14:06:36','2026-03-12 14:08:51',1),(53,32,NULL,'事假',NULL,'离校不离市','广东省-广州市-白云区-东平','2026-03-13 17:29:00','2026-03-13 22:14:00','吃饭','张德洪','18022375061',NULL,'invalidated',NULL,'刘明月','2026-03-13 10:30:38','2026-03-13 10:32:37',1),(54,32,NULL,'事假',NULL,'离校不离市','广东省-广州市-白云区-东平','2026-03-15 09:53:00','2026-03-15 17:59:00','吃饭','张德洪','18022375061',NULL,'approved',NULL,'刘明月','2026-03-15 16:54:35','2026-03-15 16:55:25',1),(55,31,NULL,'事假',NULL,'离校不离市','广东省-广州市-白云区-广警','2026-03-17 14:07:00','2026-03-17 19:07:00','看病','秦振翔','18928066081',NULL,'invalidated',NULL,'刘明月','2026-03-17 14:07:48','2026-03-17 14:08:11',1),(56,29,NULL,'事假',NULL,'离校不离市','广东省-广州市-白云区-广东警官学院','2026-03-17 14:00:00','2026-03-17 19:00:00','事假','邓肖凤','18128573832',NULL,'invalidated',NULL,'刘明月','2026-03-17 14:08:43','2026-03-17 14:20:49',1),(57,29,NULL,'事假',NULL,'离校不离市','广东省-广州市-白云区-广东警官学院','2026-03-19 15:00:00','2026-03-19 19:00:00','事假','邓肖凤','18128573832',NULL,'approved',NULL,'刘明月','2026-03-19 14:29:45','2026-03-19 14:59:01',1),(58,31,NULL,'事假',NULL,'离校不离市','广东省-广州市-白云区-广警','2026-03-19 14:29:00','2026-03-19 19:30:00','就医','秦振翔','18928066081',NULL,'approved',NULL,'刘明月','2026-03-19 14:30:03','2026-03-19 14:58:55',1),(59,34,NULL,'节假日及寒暑假请假',NULL,'离校不离市','广东省-广州市-白云区-东平','2026-03-21 12:00:00','2026-03-22 18:40:00','周末','cff','18302020725',NULL,'approved',NULL,'刘明月','2026-03-21 18:41:02','2026-03-21 18:42:24',1);
/*!40000 ALTER TABLE `leaves` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `registration_keys`
--

DROP TABLE IF EXISTS `registration_keys`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `registration_keys` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '秘钥ID',
  `salt` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '随机盐值（用于生成秘钥）',
  `username` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '关联的用户名',
  `generated_key` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '生成的秘钥（SHA256加密）',
  `generated_by` int DEFAULT NULL COMMENT '生成秘钥的管理员用户ID',
  `generated_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '秘钥生成时间',
  `used_at` datetime DEFAULT NULL COMMENT '秘钥被使用时间',
  `used_by` int DEFAULT NULL COMMENT '使用该秘钥完成验证的用户ID',
  `is_used` tinyint DEFAULT '0' COMMENT '是否已被使用 (0=未使用, 1=已使用)',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_username` (`username`),
  KEY `idx_generated_key` (`generated_key`),
  KEY `idx_is_used` (`is_used`),
  KEY `idx_generated_by` (`generated_by`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户注册验证秘钥表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `registration_keys`
--

LOCK TABLES `registration_keys` WRITE;
/*!40000 ALTER TABLE `registration_keys` DISABLE KEYS */;
INSERT INTO `registration_keys` VALUES (1,'7b65f01aa37ba812b1452b9a924c393e1ad47e4c9bfeccca5091bba0ff577e35','c2h12o2','2b81f5eb5ffc99f3d0bff7cfbf4b5065c3ee1ca4f1e91c850af495652dd2e4c9',1,'2026-01-17 15:15:19','2026-01-17 15:15:33',3,1,'2026-01-17 15:15:19'),(5,'a2ba47bf30e8c2c0a0c0180a623c790185d59ad1b8b9afcc45a18e7d4955a89e','20233502140123','f90c87115acf2c47ca98eee46c61feb319963f494d2e3d60e2d8813235215376',1,'2026-01-17 15:29:28','2026-01-17 15:41:21',2,1,'2026-01-17 15:29:28'),(7,'3c5cfcceda868873e115d10f16fb81c521b4b429b3cb565e3c346c5ea45b74d0','陈骏浩','ebc3ae10453cd840a20a5dc1b970265192bc1baa22f805e4134dd4246921f440',1,'2026-01-17 15:48:58','2026-01-17 15:49:09',10,1,'2026-01-17 15:48:58'),(8,'2d04722dfd007fe2556b09c4aec2ec2226dd36f99bcb6e69ba296831e822f339','20233502140226','033b428623803ba5eec4efef6c5719e28298675307ca3d1b1c138f073893beb8',1,'2026-01-17 15:50:25','2026-01-17 15:50:41',11,1,'2026-01-17 15:50:25'),(9,'ecb40f2b259f25e89fbf5edc683aaf2e0b66d47231711c7571a73b94f179e99d','20233502140127','c4566c67d2b13b62160eb6a1d973e1792e86163b2263d0b378d2623dc0af48f2',1,'2026-01-17 16:04:44','2026-01-17 16:05:04',12,1,'2026-01-17 16:04:44'),(10,'0799a941edc4bea9a5014c1d137107185730ceffc911543ef649bcdbb829119c','20233502140127','d68f2ccc39c1f17bde9711c318883d17648ddab86df05b75e47ea27fa110f4f9',1,'2026-01-17 16:10:38',NULL,NULL,0,'2026-01-17 16:10:38'),(11,'3d4eea5f708955365a7a2469aa50f4f0b47fa6b58c9fe9ed51edea20fc002db8','10086','ac34d4c5a05a364df2a2d972867a13c7e288085c921541e0d4af2867ea9ee2c3',1,'2026-01-17 16:31:31','2026-01-17 16:32:04',14,1,'2026-01-17 16:31:31'),(12,'29ce7eadc6aa74b3a032692dd841cbfb629554686e01b739a2ce2e8bb31fd14c','20233502140114','f31040176dc337bca3fe24e3cd2262cd2ca767a24ec7a514e62c0f9aa7464498',1,'2026-01-17 16:47:28','2026-01-17 16:47:54',15,1,'2026-01-17 16:47:28'),(13,'e632be3bf6fe5124e6ce149c6e3e53b26d1b9fb7f7f4eb18defbb18d50f718e3','1','0ab1bc0724ff2089be7d9999bcfa73020b7551691f739b629f83771dd1eb3f2d',1,'2026-01-17 16:56:15','2026-01-17 16:57:21',16,1,'2026-01-17 16:56:15'),(14,'ad8d4287a62d548e9e1a885f40c0a4fba5b2d23bc5cbbff3911acb2d126fc252','neriasw','1ec52ec7c697547eb3f32345a5b1142c6b99d8dd3fb04a8f7a220c1e7d8c4948',1,'2026-01-17 18:11:57','2026-01-17 18:12:24',18,1,'2026-01-17 18:11:57'),(15,'3878cb9d0c65ba42e5151e0690f4eb4a48b01ace558cc5bc9a4e5b941acba5ad','zzw','b83f88d936e94c501daaf8acd5421f990b8ebc359a5f4c0a98612226ae9ff854',1,'2026-01-17 20:54:16','2026-01-17 20:54:28',19,1,'2026-01-17 20:54:16'),(16,'62c02f284b4f3980e79c0f3a5d24e308c303ca4730d3cf881fdca11215d78c77','cff','d1a5f99c7ab0a83a882c78b6ee4da6ad40699d193a17785490aa0b3405f0a7ac',1,'2026-01-18 00:18:27','2026-01-18 00:18:47',20,1,'2026-01-18 00:18:27'),(17,'5e5bacb37455c50b0cd894b4f4351aaed02483f281ec61194506c3ee934c271d','113','474b94fe3700c3fdf5f18b77c85410085cf24ec4d10c17f840b0b90b3aa3d00a',1,'2026-01-18 00:42:16','2026-01-18 00:42:35',21,1,'2026-01-18 00:42:16'),(18,'5cb5cbf8cd29e91353ba4635c325d0c0ece22b23c4be94a40c99f7f54aaab830','6','bdff3a2ddebbf0dd61f20eda8867b74e319997c943fa9156892ed2c0823faa59',1,'2026-01-18 16:55:50','2026-01-18 17:10:43',23,1,'2026-01-18 16:55:50'),(19,'042c8cdd40005725bd29fc5359044562abb53051961e1840fed3a9f76cac7dbc','20233502140135','dc93db4c412e27fbf181cdc01c4e859ca41da8af64cffbcd85d8a68f577219d0',1,'2026-01-19 20:20:25','2026-01-19 20:20:38',24,1,'2026-01-19 20:20:25'),(20,'5e917c767befdf2493455c450a226d03798d932ad9909bd082266f168bf2f1c8','20243502140128','17b77f4368353a3ac723eaa5fa24e6f4b9d12d6fbd0d6cb5863fb3cad30718ca',1,'2026-01-19 20:23:33','2026-01-19 20:23:49',25,1,'2026-01-19 20:23:33'),(21,'6be5c41eabf621fe0accd1f4f2baf836cc5580921a60193b27d48c5eb7e765fd','sunrise','0a94c5a8ab85cc50603668e5572db1ff173ad66ca93e1ea9fba5242dd570ec33',1,'2026-01-20 12:16:16','2026-01-20 12:16:31',27,1,'2026-01-20 12:16:16'),(22,'08702360ba8c80dda8407b314bcb6807b7f943ef1053424841ddd63c78d21abf','橙子','41b876a0e2f389686f3a411caad26803c1700f2c06b33b114ad0832e330a5aed',1,'2026-01-20 14:39:55','2026-01-20 14:40:06',28,1,'2026-01-20 14:39:55'),(23,'bc9aa31e48de9d17b4e3c339703b69067e82542b83ac417c7c51cec3ab856654','20233502140115','12ee8b89843e64ea8822410905db69894b0abb265741d230c771888ae8a59cfd',1,'2026-03-05 09:08:11','2026-03-05 09:08:25',29,1,'2026-03-05 09:08:11'),(24,'7ef006b33f3d76b8d7694087d275a1fd81399f5e449641aaf83a0974fbdb734a','114','5567fbc6b791445e665db6e54e75a7e80fdfeac42f10a14863a28d20417e2aef',1,'2026-03-10 16:39:18','2026-03-10 16:39:29',31,1,'2026-03-10 16:39:18'),(25,'60a07964ff27fd31089f86723df7277967d4c9faa27815e7886e7441812a531a','张志炜','db85c80afb5d884ac9661d468f5dbe283b91096031601446e4808554831acc58',1,'2026-03-13 10:24:54','2026-03-13 10:25:07',32,1,'2026-03-13 10:24:54'),(26,'3b42e9d403447d0a1a22039b999f58f0148e0cc4750b44bcc74e3a3ed73aadbd','20253502140113','c565bacd90641f40678088a8a9b37f5de52176595b96e8bf7430e5de9ae67b99',1,'2026-03-21 18:39:09','2026-03-21 18:39:24',34,1,'2026-03-21 18:39:09'),(27,'972a61d498bf89ed12f43dfc14c9599feae0fea08039d72ce0515691a3c8978f','20233502140116','87d86de2b49e80be5c99a34f0a8d721aa3b520a5d4cf71ca52872a19a8f5eedc',1,'2026-03-21 18:43:17',NULL,NULL,0,'2026-03-21 18:43:17'),(28,'89a911ab16b0d8b6f87b7ad3fe9d60551e1d4d0fd073078fbcf9e1f40f644668','20233502140116','bd6ae03f467e58ab07524652c980a80cdb04f1641bc25cf9c8b199982531f499',1,'2026-03-21 18:44:20',NULL,NULL,0,'2026-03-21 18:44:20');
/*!40000 ALTER TABLE `registration_keys` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `username` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用户名（唯一）',
  `password` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '密码（SHA256加密）',
  `name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '姓名',
  `gender` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '性别',
  `department` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '院系/部门',
  `major` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '专业',
  `student_id` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '学号',
  `year` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '年级',
  `class_name` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '班级',
  `phone` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '联系电话',
  `role` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'student' COMMENT '角色: student(学生) 或 admin(管理员)',
  `status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'verified' COMMENT 'verified(已验证), pending(待验证), rejected(已拒绝/锁定)',
  `verification_key` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '用户验证秘钥',
  `verified_at` datetime DEFAULT NULL COMMENT '验证完成时间',
  `profile_completed` tinyint DEFAULT '0' COMMENT '个人信息是否完善 (0=未完善, 1=已完善)',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '账户创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `ux_username` (`username`),
  UNIQUE KEY `ux_users_username` (`username`),
  KEY `idx_role` (`role`),
  KEY `idx_status` (`status`),
  KEY `idx_profile_completed` (`profile_completed`)
) ENGINE=InnoDB AUTO_INCREMENT=39 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'admin','fe92795d0d48538dfe88e715ac0b896fd2d0fca22630466d18273b574e0e7657','系统管理员','male','学工部',NULL,NULL,NULL,NULL,NULL,'admin','verified',NULL,'2026-01-17 15:00:29',1,'2026-01-17 15:00:29','2026-01-17 15:00:29'),(2,'20233502140123','8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92','麦恺晖',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'student','verified','f90c87115acf2c47ca98eee46c61feb319963f494d2e3d60e2d8813235215376','2026-01-17 15:41:21',0,'2026-01-17 15:11:35','2026-01-17 15:41:21'),(3,'c2h12o2','abb77525ab2094522408476f77709c7ee617b1f2e2dd75b73ad98e2abe34aea4','陈子兴',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'student','verified','2b81f5eb5ffc99f3d0bff7cfbf4b5065c3ee1ca4f1e91c850af495652dd2e4c9','2026-01-17 15:15:33',0,'2026-01-17 15:14:57','2026-01-17 15:15:33'),(10,'陈骏浩','960fa235a1ba531e040aee5626127669f1e461a5f11096941064c8f88089d810','陈骏浩',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'student','verified','ebc3ae10453cd840a20a5dc1b970265192bc1baa22f805e4134dd4246921f440','2026-01-17 15:49:09',0,'2026-01-17 15:48:57','2026-01-17 15:49:09'),(11,'20233502140226','8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92','黎嘉聪','男','网络安全学院','网络安全与执法','','2023','2023网络安全与执法二区队','13702373051','student','verified','033b428623803ba5eec4efef6c5719e28298675307ca3d1b1c138f073893beb8','2026-01-17 15:50:41',1,'2026-01-17 15:49:24','2026-01-17 15:51:43'),(12,'20233502140127','8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92','王廖聪','男','网络安全学院','网络安全与执法','20233502140127','2023','2023网络安全与执法一区队','13723473486','student','verified','c4566c67d2b13b62160eb6a1d973e1792e86163b2263d0b378d2623dc0af48f2','2026-01-17 16:05:04',1,'2026-01-17 16:04:39','2026-01-17 16:06:38'),(14,'10086','caf307135ea8fd58af876d92eca4043c8721ca88824078bad3215dccd148cb36','龙杰飞','男','网络安全学院','网络安全与执法','20243502140420','2024','2024网络安全与执法四区队','13726430244','student','verified','ac34d4c5a05a364df2a2d972867a13c7e288085c921541e0d4af2867ea9ee2c3','2026-01-17 16:32:04',1,'2026-01-17 16:31:09','2026-01-17 16:33:20'),(15,'20233502140114','1a19eebaba1822e0d8e8f221655143a9e6cf5b0f010426b22e1a34273f1dc15c','秦振翔','男','网络安全学院','网络安全与执法','20233502140114','2023','网络安全执法一区队','18928066081','student','verified','f31040176dc337bca3fe24e3cd2262cd2ca767a24ec7a514e62c0f9aa7464498','2026-01-17 16:47:54',1,'2026-01-17 16:47:25','2026-01-17 16:49:50'),(16,'1','8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92','钟梓荣',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'student','verified','0ab1bc0724ff2089be7d9999bcfa73020b7551691f739b629f83771dd1eb3f2d','2026-01-17 16:57:21',0,'2026-01-17 16:55:53','2026-01-17 16:57:21'),(18,'neriasw','00a0432b978fa7f7b6701510347fbe9870a8c04d113e2ffc492c7030947669f4','曾兆康','','网络安全学院','网络安全与执法','20233502140213','2023','2023级网络安全与执法实验班','15626962305','student','verified','1ec52ec7c697547eb3f32345a5b1142c6b99d8dd3fb04a8f7a220c1e7d8c4948','2026-01-17 18:12:24',1,'2026-01-17 18:11:40','2026-01-17 18:13:23'),(20,'cff','8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92','曹丰凡','男','网络安全学院','网络安全与执法','20233502140116','2023','2023网络安全与执法一区队','15975443636','student','verified','d1a5f99c7ab0a83a882c78b6ee4da6ad40699d193a17785490aa0b3405f0a7ac','2026-01-18 00:18:47',1,'2026-01-18 00:18:22','2026-01-18 00:20:03'),(23,'6','bcb15f821479b4d5772bd0ca866c00ad5f926e3580720659cc80d39c9d09802a','卢韵','女','网络安全学院','网络安全与执法','20233502140138','2023','2023网络安全与执法一区队','13532111209','student','verified','bdff3a2ddebbf0dd61f20eda8867b74e319997c943fa9156892ed2c0823faa59','2026-01-18 17:10:43',1,'2026-01-18 16:46:49','2026-01-18 17:11:32'),(24,'20233502140135','6c5d61a587bbadd1174bf2380c755c6a5796b7cea4b32673760316f4fa16e219','刘子慧','女','网络安全学院','网络安全与执法','20233502140135','2023','2023网络安全与执法一区队','15011648538','student','verified','dc93db4c412e27fbf181cdc01c4e859ca41da8af64cffbcd85d8a68f577219d0','2026-01-19 20:20:38',1,'2026-01-19 20:20:01','2026-01-19 20:21:25'),(25,'20243502140128','8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92','彭渤',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'student','verified','17b77f4368353a3ac723eaa5fa24e6f4b9d12d6fbd0d6cb5863fb3cad30718ca','2026-01-19 20:23:49',0,'2026-01-19 20:21:39','2026-01-19 20:23:49'),(27,'sunrise','371e075a94c67359d6c78d31b7fa73ee7e30bcdbe447f63e4dc65012fa6eae16','柯文博',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'student','verified','0a94c5a8ab85cc50603668e5572db1ff173ad66ca93e1ea9fba5242dd570ec33','2026-01-20 12:16:31',0,'2026-01-20 12:15:50','2026-01-20 12:16:31'),(28,'橙子','8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92','陈梓铭','男','网络安全学院','网络安全与执法','202233502140330','2023','2023网络安全与执法二区队','','student','verified','41b876a0e2f389686f3a411caad26803c1700f2c06b33b114ad0832e330a5aed','2026-01-20 14:40:06',1,'2026-01-20 14:39:32','2026-01-20 14:41:40'),(29,'20233502140115','34c73358d124040b8b3893532ecb2a24c6a91969265b79525998a063a9022823','洪易','','网络安全学院','网络安全与执法','20233502140115','2023','2023网络安全与执法一区队','13316665001','student','verified','12ee8b89843e64ea8822410905db69894b0abb265741d230c771888ae8a59cfd','2026-03-05 09:08:25',1,'2026-03-05 09:07:25','2026-03-05 09:09:44'),(31,'114','d94a2f06ddb030b79cd0f1a959295cea3826bfaca2a53e1e6f8907777fea8856','秦振翔',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'student','verified','5567fbc6b791445e665db6e54e75a7e80fdfeac42f10a14863a28d20417e2aef','2026-03-10 16:39:29',0,'2026-03-10 16:38:58','2026-03-10 16:39:29'),(32,'张志炜','b367d84c1b54f61b88bc937762c6360a9bf1646bc24b50f25baccf6976c608c1','张志炜','男','网络安全学院','网络安全与执法','20233502140325','2023','2023网络安全与执法二区队','13660177883','student','verified','db85c80afb5d884ac9661d468f5dbe283b91096031601446e4808554831acc58','2026-03-13 10:25:07',1,'2026-03-13 10:23:49','2026-03-13 10:29:04'),(34,'20253502140113','8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92','林光辉',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'student','verified','c565bacd90641f40678088a8a9b37f5de52176595b96e8bf7430e5de9ae67b99','2026-03-21 18:39:24',0,'2026-03-21 18:38:06','2026-03-21 18:39:24');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-23 11:09:57
