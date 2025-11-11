package com.example.nsepulse.service.dto;

import lombok.Getter;
import lombok.Setter;

import java.util.List;
import java.util.Map;

@Getter
@Setter
public class StockPerformanceDTO {

    private String stockName;
    private String currentPrice;
    private String todayPercent;
    private String oneWeekPercent;
    private String oneMonthPercent;
    private String twoMonthsPercent;
    private String threeMonthsPercent;
    private List<Double> sparklineData;

    public StockPerformanceDTO(Map<String, Object> performanceData) {
        this.stockName = (String) performanceData.get("Stock Name");
        this.currentPrice = (String) performanceData.get("Current Price");
        this.todayPercent = (String) performanceData.get("Today %");
        this.oneWeekPercent = (String) performanceData.get("1 Week %");
        this.oneMonthPercent = (String) performanceData.get("1 Month %");
        this.twoMonthsPercent = (String) performanceData.get("2 Months %");
        this.threeMonthsPercent = (String) performanceData.get("3 Months %");
        this.sparklineData = (List<Double>) performanceData.get("sparkline_data");
    }

    // Getters and setters
}
