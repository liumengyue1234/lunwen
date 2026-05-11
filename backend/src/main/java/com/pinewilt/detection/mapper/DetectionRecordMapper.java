package com.pinewilt.detection.mapper;

import com.pinewilt.detection.entity.DetectionRecord;
import org.apache.ibatis.annotations.*;
import java.util.List;

@Mapper
public interface DetectionRecordMapper {

    @Insert("INSERT INTO detection_record(filename, file_path, file_size, status) " +
            "VALUES(#{filename}, #{filePath}, #{fileSize}, #{status})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(DetectionRecord record);

    @Update("UPDATE detection_record SET " +
            "has_lesion=#{hasLesion}, lesion_ratio=#{lesionRatio}, " +
            "lesion_pixels=#{lesionPixels}, total_pixels=#{totalPixels}, " +
            "confidence=#{confidence}, mask_path=#{maskPath}, overlay_path=#{overlayPath}, " +
            "status=#{status}, error_msg=#{errorMsg} WHERE id=#{id}")
    int update(DetectionRecord record);

    @Select("SELECT * FROM detection_record ORDER BY created_at DESC LIMIT #{limit} OFFSET #{offset}")
    List<DetectionRecord> findPage(@Param("limit") int limit, @Param("offset") int offset);

    @Select("SELECT COUNT(*) FROM detection_record")
    int countAll();

    @Select("SELECT * FROM detection_record WHERE id=#{id}")
    DetectionRecord findById(Long id);

    @Select("SELECT COUNT(*) FROM detection_record WHERE has_lesion=true")
    int countPositive();

    @Select("SELECT AVG(confidence) FROM detection_record WHERE status='SUCCESS'")
    Double avgConfidence();
}
