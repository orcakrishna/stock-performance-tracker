package com.example.nsepulse.service.impl;

import com.example.nsepulse.StockDataFetcher;
import com.example.nsepulse.service.StockService;
import com.example.nsepulse.service.dto.StockPerformanceDTO;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
public class StockServiceImpl implements StockService {

    @Override
    @Cacheable(value = "stockPerformance", key = "#ticker")
    public Optional<StockPerformanceDTO> getStockPerformance(String ticker) {
        Map<String, Object> performanceData = StockDataFetcher.getStockPerformance(ticker);
        if (performanceData.isEmpty()) {
            return Optional.empty();
        }
        return Optional.of(new StockPerformanceDTO(performanceData));
    }

    @Override
    public List<String> getStockTickersFromFile(MultipartFile file) throws IOException {
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(file.getInputStream()))) {
            return reader.lines().map(String::trim).filter(line -> !line.isEmpty()).collect(Collectors.toList());
        }
    }
}
