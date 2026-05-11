package com.pinewilt.detection.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.pinewilt.detection.entity.DetectionRecord;
import com.pinewilt.detection.mapper.DetectionRecordMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import okhttp3.*;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;

@Slf4j
@Service
@RequiredArgsConstructor
public class DetectionService {

    private final DetectionRecordMapper mapper;
    private final OkHttpClient httpClient;
    private final ObjectMapper objectMapper = new ObjectMapper();

    @Value("${inference.server.url:http://localhost:8000}")
    private String inferenceUrl;

    @Value("${file.upload.path:./uploads}")
    private String uploadPath;

    @Value("${file.result.path:./results}")
    private String resultPath;

    /**
     * 上传CT图像并执行检测
     */
    public DetectionRecord detect(MultipartFile file) throws IOException {
        // 1. 创建存储目录
        Files.createDirectories(Paths.get(uploadPath));
        Files.createDirectories(Paths.get(resultPath));

        // 2. 保存上传文件
        String filename = System.currentTimeMillis() + "_" + file.getOriginalFilename();
        Path filePath = Paths.get(uploadPath, filename);
        file.transferTo(filePath);

        // 3. 插入待处理记录
        DetectionRecord record = new DetectionRecord();
        record.setFilename(file.getOriginalFilename());
        record.setFilePath(filePath.toString());
        record.setFileSize(file.getSize());
        record.setStatus("PENDING");
        mapper.insert(record);
        log.info("创建检测记录 ID={}, 文件={}", record.getId(), filename);

        // 4. 调用Python推理服务
        try {
            JsonNode result = callInferenceService(filePath.toFile());
            record.setHasLesion(result.get("lesion_detected").asBoolean());
            record.setLesionRatio(result.get("lesion_ratio").asDouble());
            record.setLesionPixels(result.get("lesion_pixels").asInt());
            record.setTotalPixels(result.get("total_pixels").asInt());
            record.setConfidence(result.get("confidence").asDouble());

            // 保存掩码图和叠加图
            String maskB64 = result.get("mask_base64").asText();
            String overlayB64 = result.get("overlay_base64").asText();
            String maskName = "mask_" + record.getId() + ".png";
            String overlayName = "overlay_" + record.getId() + ".png";
            saveBase64Image(maskB64, Paths.get(resultPath, maskName));
            saveBase64Image(overlayB64, Paths.get(resultPath, overlayName));

            record.setMaskPath("/results/" + maskName);
            record.setOverlayPath("/results/" + overlayName);
            record.setStatus("SUCCESS");
            log.info("检测成功 ID={}, 病变={}, 面积比={:.4f}",
                    record.getId(), record.getHasLesion(), record.getLesionRatio());

        } catch (Exception e) {
            log.error("推理服务调用失败: {}", e.getMessage(), e);
            record.setStatus("FAILED");
            record.setErrorMsg(e.getMessage());
        }

        // 5. 更新记录
        mapper.update(record);
        return record;
    }

    /**
     * 查询检测历史（分页）
     */
    public Map<String, Object> getHistory(int page, int pageSize) {
        int offset = (page - 1) * pageSize;
        List<DetectionRecord> records = mapper.findPage(pageSize, offset);
        int total = mapper.countAll();

        Map<String, Object> result = new HashMap<>();
        result.put("records", records);
        result.put("total", total);
        result.put("page", page);
        result.put("pageSize", pageSize);
        result.put("totalPages", (int) Math.ceil((double) total / pageSize));
        return result;
    }

    /**
     * 获取系统统计
     */
    public Map<String, Object> getStats() {
        int total = mapper.countAll();
        int positive = mapper.countPositive();
        Double avgConf = mapper.avgConfidence();

        Map<String, Object> stats = new HashMap<>();
        stats.put("totalDetections", total);
        stats.put("positiveCases", positive);
        stats.put("negativeCases", total - positive);
        stats.put("positiveRate", total > 0 ? (double) positive / total : 0.0);
        stats.put("avgConfidence", avgConf != null ? avgConf : 0.0);
        return stats;
    }

    /**
     * 获取单条记录
     */
    public DetectionRecord getById(Long id) {
        return mapper.findById(id);
    }

    /**
     * 调用Python推理服务
     */
    private JsonNode callInferenceService(File imageFile) throws IOException {
        RequestBody requestBody = new MultipartBody.Builder()
                .setType(MultipartBody.FORM)
                .addFormDataPart("file", imageFile.getName(),
                        RequestBody.create(imageFile, MediaType.parse("image/png")))
                .build();

        Request request = new Request.Builder()
                .url(inferenceUrl + "/predict")
                .post(requestBody)
                .build();

        try (Response response = httpClient.newCall(request).execute()) {
            if (!response.isSuccessful()) {
                throw new IOException("推理服务返回错误: " + response.code());
            }
            String body = response.body().string();
            return objectMapper.readTree(body);
        }
    }

    /**
     * 保存Base64编码图像
     */
    private void saveBase64Image(String base64, Path path) throws IOException {
        byte[] imageBytes = Base64.getDecoder().decode(base64);
        Files.write(path, imageBytes);
    }
}
