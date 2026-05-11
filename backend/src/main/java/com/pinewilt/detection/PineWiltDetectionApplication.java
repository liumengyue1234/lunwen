package com.pinewilt.detection;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan("com.pinewilt.detection.mapper")
public class PineWiltDetectionApplication {

    public static void main(String[] args) {
        SpringApplication.run(PineWiltDetectionApplication.class, args);
    }
}
