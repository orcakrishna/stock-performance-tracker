package com.example.nsepulse.service;

import com.example.nsepulse.service.dto.StockPerformanceDTO;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.List;
import java.util.Optional;

public interface StockService {
    Optional<StockPerformanceDTO> getStockPerformance(String ticker);
    List<String> getStockTickersFromFile(MultipartFile file) throws IOException;
}
