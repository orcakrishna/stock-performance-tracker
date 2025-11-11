import React, { useState } from 'react';
import axios from 'axios';
import StockPerformance from './components/StockPerformance';
import FileUpload from './components/FileUpload';
import './App.css';

function App() {
    const [ticker, setTicker] = useState('');
    const [stock, setStock] = useState(null);
    const [error, setError] = useState('');

    const getStockData = () => {
        axios.get(`/api/stocks/${ticker}`)
            .then(response => {
                setStock(response.data);
                setError('');
            })
            .catch(err => {
                setStock(null);
                setError('Error fetching stock data');
            });
    };

    return (
        <div className="App">
            <header className="App-header">
                <h1>NSE Pulse</h1>
                <div className="search-bar">
                    <input
                        type="text"
                        value={ticker}
                        onChange={(e) => setTicker(e.target.value)}
                        placeholder="Enter stock ticker"
                    />
                    <button onClick={getStockData}>Get Performance</button>
                </div>
                {error && <p className="error">{error}</p>}
                {stock && <StockPerformance stock={stock} />}
                <FileUpload />
            </header>
        </div>
    );
}

export default App;
