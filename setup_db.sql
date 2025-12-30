-- MySQL 데이터베이스 생성 스크립트
-- UTF-8 인코딩을 사용하여 한글 및 이모지 지원

-- 데이터베이스 생성 (이미 존재하면 삭제 후 재생성)
DROP DATABASE IF EXISTS marine_real_estate;
CREATE DATABASE marine_real_estate
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- 데이터베이스 선택
USE marine_real_estate;

-- 사용자 생성 (선택사항 - 보안을 위해 별도 사용자 생성 권장)
-- CREATE USER IF NOT EXISTS 'marine_user'@'localhost' IDENTIFIED BY 'your_password';
-- GRANT ALL PRIVILEGES ON marine_real_estate.* TO 'marine_user'@'localhost';
-- FLUSH PRIVILEGES;

-- 데이터베이스 설정 확인
SELECT
    DEFAULT_CHARACTER_SET_NAME,
    DEFAULT_COLLATION_NAME
FROM information_schema.SCHEMATA
WHERE SCHEMA_NAME = 'marine_real_estate';
