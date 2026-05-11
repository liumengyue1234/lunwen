package com.pinewilt.detection.entity;

import lombok.Data;
import java.time.LocalDateTime;

/**
 * 系统统计实体
 */
@Data
public class SystemStats {
    private Long id;
    private Integer totalDetections;
    private Integer positiveCases;
    private Integer negativeCases;
    private Double avgConfidence;
    private LocalDateTime updatedAt;
}
