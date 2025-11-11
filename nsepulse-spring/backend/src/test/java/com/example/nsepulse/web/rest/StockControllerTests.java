package com.example.nsepulse.web.rest;

import com.example.nsepulse.service.StockService;
import com.example.nsepulse.service.dto.StockPerformanceDTO;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.web.servlet.MockMvc;

import java.util.Optional;

import static org.mockito.BDDMockito.given;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(StockController.class)
public class StockControllerTests {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private StockService stockService;

    @Test
    public void getStockPerformance_returnsOk() throws Exception {
        StockPerformanceDTO stockPerformanceDTO = new StockPerformanceDTO(java.util.Collections.emptyMap());
        given(stockService.getStockPerformance("RELIANCE.NS")).willReturn(Optional.of(stockPerformanceDTO));

        mockMvc.perform(get("/api/stocks/RELIANCE.NS"))
                .andExpect(status().isOk());
    }
}
