package com.example.nsepulse.web.rest;

import com.example.nsepulse.service.StockService;
import com.example.nsepulse.service.dto.StockPerformanceDTO;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.List;

@RestController
@RequestMapping("/api/stocks")
public class StockController {

    private final StockService stockService;

    public StockController(StockService stockService) {
        this.stockService = stockService;
    }

    @GetMapping("/{ticker}")
    public ResponseEntity<StockPerformanceDTO> getStockPerformance(@PathVariable String ticker) {
        return stockService.getStockPerformance(ticker)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping("/upload")
    public ResponseEntity<?> uploadFile(@RequestParam("file") MultipartFile file) {
        try {
            List<String> tickers = stockService.getStockTickersFromFile(file);
            return ResponseEntity.ok(tickers);
        } catch (IOException e) {
            return ResponseEntity.badRequest().body(new FileUploadResponse("Error processing file"));
        }
    }
}
