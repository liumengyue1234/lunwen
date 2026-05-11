package com.pinewilt.detection.controller;

import com.pinewilt.detection.entity.DetectionRecord;
import com.pinewilt.detection.service.DetectionService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.HashMap;
import java.util.Map;

/**
 * 检测接口控制器
 */
@Slf4j
@RestController
@RequestMapping("/detection")
@RequiredArgsConstructor
public class DetectionController {

    private final DetectionService detectionService;

    /**
     * 上传CT图像进行病变检测
     * POST /api/detection/upload
     */
    @PostMapping("/upload")
    public ResponseEntity<Map<String, Object>> upload(
            @RequestParam("file") MultipartFile file) {

        Map<String, Object> response = new HashMap<>();
        
        if (file.isEmpty()) {
            response.put("success", false);
            response.put("message", "请选择要上传的文件");
            return ResponseEntity.badRequest().body(response);
        }

        // 校验文件类型
        String contentType = file.getContentType();
        if (contentType == null || (!contentType.startsWith("image/"))) {
            response.put("success", false);
            response.put("message", "请上传图像文件（PNG/JPEG/TIFF）");
            return ResponseEntity.badRequest().body(response);
        }

        try {
            DetectionRecord record = detectionService.detect(file);
            response.put("success", true);
            response.put("message", "检测完成");
            response.put("data", record);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            log.error("检测失败", e);
            response.put("success", false);
            response.put("message", "检测失败: " + e.getMessage());
            return ResponseEntity.internalServerError().body(response);
        }
    }

    /**
     * 获取检测历史记录
     * GET /api/detection/history?page=1&pageSize=10
     */
    @GetMapping("/history")
    public ResponseEntity<Map<String, Object>> getHistory(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int pageSize) {

        Map<String, Object> response = new HashMap<>();
        try {
            Map<String, Object> data = detectionService.getHistory(page, pageSize);
            response.put("success", true);
            response.put("data", data);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            response.put("success", false);
            response.put("message", e.getMessage());
            return ResponseEntity.internalServerError().body(response);
        }
    }

    /**
     * 获取单条检测记录
     * GET /api/detection/{id}
     */
    @GetMapping("/{id}")
    public ResponseEntity<Map<String, Object>> getById(@PathVariable Long id) {
        Map<String, Object> response = new HashMap<>();
        DetectionRecord record = detectionService.getById(id);
        if (record == null) {
            response.put("success", false);
            response.put("message", "记录不存在");
            return ResponseEntity.notFound().build();
        }
        response.put("success", true);
        response.put("data", record);
        return ResponseEntity.ok(response);
    }

    /**
     * 系统统计信息
     * GET /api/detection/stats
     */
    @GetMapping("/stats")
    public ResponseEntity<Map<String, Object>> getStats() {
        Map<String, Object> response = new HashMap<>();
        try {
            Map<String, Object> stats = detectionService.getStats();
            response.put("success", true);
            response.put("data", stats);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            response.put("success", false);
            response.put("message", e.getMessage());
            return ResponseEntity.internalServerError().body(response);
        }
    }

    /**
     * 健康检查
     * GET /api/detection/health
     */
    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> health() {
        Map<String, Object> response = new HashMap<>();
        response.put("status", "UP");
        response.put("service", "pine-wilt-detection-backend");
        return ResponseEntity.ok(response);
    }
}
