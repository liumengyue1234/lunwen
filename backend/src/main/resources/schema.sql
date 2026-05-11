-- 松材线虫病检测系统数据库初始化脚本

-- 检测记录表
CREATE TABLE IF NOT EXISTS detection_record (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    filename    VARCHAR(255) NOT NULL COMMENT '原始文件名',
    file_path   VARCHAR(512) NOT NULL COMMENT '存储路径',
    file_size   BIGINT       COMMENT '文件大小(字节)',
    has_lesion  BOOLEAN      DEFAULT FALSE COMMENT '是否检测到病变',
    lesion_ratio DOUBLE      DEFAULT 0.0  COMMENT '病变面积比例',
    lesion_pixels INT        DEFAULT 0    COMMENT '病变像素数',
    total_pixels  INT        DEFAULT 0    COMMENT '总像素数',
    confidence  DOUBLE       DEFAULT 0.0  COMMENT '置信度',
    mask_path   VARCHAR(512) COMMENT '掩码图存储路径',
    overlay_path VARCHAR(512) COMMENT '叠加图存储路径',
    status      VARCHAR(20)  DEFAULT 'PENDING' COMMENT '处理状态: PENDING/SUCCESS/FAILED',
    error_msg   TEXT         COMMENT '错误信息',
    created_at  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 系统统计表
CREATE TABLE IF NOT EXISTS system_stats (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    total_detections INT DEFAULT 0 COMMENT '总检测次数',
    positive_cases   INT DEFAULT 0 COMMENT '阳性病例数',
    negative_cases   INT DEFAULT 0 COMMENT '阴性病例数',
    avg_confidence   DOUBLE DEFAULT 0.0 COMMENT '平均置信度',
    updated_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
