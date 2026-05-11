package com.pinewilt.detection.entity;

import lombok.Data;
import java.time.LocalDateTime;

/**
 * 检测记录实体
 */
@Data
public class DetectionRecord {
    private Long id;
    private String filename;
    private String filePath;
    private Long fileSize;
    private Boolean hasLesion;
    private Double lesionRatio;
    private Integer lesionPixels;
    private Integer totalPixels;
    private Double confidence;
    private String maskPath;
    private String overlayPath;
    private String status;   // PENDING / SUCCESS / FAILED
    private String errorMsg;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
