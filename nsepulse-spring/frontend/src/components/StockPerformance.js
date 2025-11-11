import React from 'react';

const StockPerformance = ({ stock }) => {
    return (
        <div className="stock-performance">
            <h3>{stock.stockName}</h3>
            <p>Current Price: {stock.currentPrice}</p>
            <p>Today: {stock.todayPercent}%</p>
            <p>1 Week: {stock.oneWeekPercent}%</p>
            <p>1 Month: {stock.oneMonthPercent}%</p>
            <p>2 Months: {stock.twoMonthsPercent}%</p>
            <p>3 Months: {stock.threeMonthsPercent}%</p>
        </div>
    );
};

export default StockPerformance;
