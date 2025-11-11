package com.example.nsepulse;

import yahoofinance.Stock;
import yahoofinance.YahooFinance;
import yahoofinance.histquotes.HistoricalQuote;
import yahoofinance.histquotes.Interval;

import java.math.BigDecimal;
import java.util.*;
import java.util.stream.Collectors;

public class StockDataFetcher {

    public static Map<String, Object> getStockPerformance(String ticker) {
        try {
            Stock stock = YahooFinance.get(ticker, true);
            if (stock == null) {
                return Collections.emptyMap();
            }

            List<HistoricalQuote> historicalQuotes = stock.getHistory(Interval.DAILY);
            if (historicalQuotes.isEmpty()) {
                return Collections.emptyMap();
            }

            BigDecimal currentPrice = stock.getQuote().getPrice();
            BigDecimal previousClose = stock.getQuote().getPreviousClose();
            BigDecimal changeToday = stock.getQuote().getChangeInPercent();

            Map<String, Object> performanceData = new HashMap<>();
            performanceData.put("Stock Name", stock.getName());
            performanceData.put("Current Price", "₹" + String.format("%.2f", currentPrice));
            performanceData.put("Today %", String.format("%.2f", changeToday));
            performanceData.put("1 Week %", getPerformanceByDays(historicalQuotes, currentPrice, 7));
            performanceData.put("1 Month %", getPerformanceByDays(historicalQuotes, currentPrice, 30));
            performanceData.put("2 Months %", getPerformanceByDays(historicalQuotes, currentPrice, 60));
            performanceData.put("3 Months %", getPerformanceByDays(historicalQuotes, currentPrice, 90));

            List<Double> sparklineData = historicalQuotes.stream()
                    .map(quote -> quote.getClose().doubleValue())
                    .collect(Collectors.toList());

            if (sparklineData.size() >= 30) {
                sparklineData = sparklineData.subList(sparklineData.size() - 30, sparklineData.size());
            }

            performanceData.put("sparkline_data", normalizeSparkline(sparklineData));

            return performanceData;
        } catch (Exception e) {
            e.printStackTrace();
            return Collections.emptyMap();
        }
    }

    private static String getPerformanceByDays(List<HistoricalQuote> quotes, BigDecimal currentPrice, int days) {
        Calendar from = Calendar.getInstance();
        from.add(Calendar.DAY_OF_MONTH, -days);

        BigDecimal pastPrice = quotes.stream()
                .filter(q -> q.getDate().before(from))
                .findFirst()
                .map(HistoricalQuote::getClose)
                .orElse(quotes.get(0).getClose());

        BigDecimal performance = (currentPrice.subtract(pastPrice)).divide(pastPrice, 4, BigDecimal.ROUND_HALF_UP).multiply(BigDecimal.valueOf(100));
        return String.format("%.2f", performance);
    }

    private static List<Double> normalizeSparkline(List<Double> sparklinePrices) {
        if (sparklinePrices == null || sparklinePrices.isEmpty()) {
            return Collections.emptyList();
        }

        double minPrice = Collections.min(sparklinePrices);
        double maxPrice = Collections.max(sparklinePrices);
        double priceRange = maxPrice - minPrice;

        if (priceRange > 0) {
            return sparklinePrices.stream()
                    .map(p -> ((p - minPrice) / priceRange) * 100)
                    .collect(Collectors.toList());
        } else {
            return sparklinePrices.stream().map(p -> 50.0).collect(Collectors.toList());
        }
    }
}
