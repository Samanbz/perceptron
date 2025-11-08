"""
Peers Newsroom APIs - Financial Data Integration

This module provides real financial data for the peers newsroom functionality,
replacing mock/scraped data with dedicated financial APIs.

APIs Integrated:
- Alpha Vantage: Stock data, earnings, financial statements, earnings call transcripts
- Financial Modeling Prep: Company profiles, earnings reports, press releases, financial statements
- Polygon.io: Market news, real-time trades, financial market data
- Finnhub: Company profiles, basic financials, market data
- Twelve Data: Real-time quotes, historical data, technical indicators

All APIs are free tier with reasonable rate limits.
"""

import os
import requests
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

# Load environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

logger = logging.getLogger(__name__)

class PeersNewsroomAPIs:
    """
    Aggregates financial data from multiple APIs for peers newsroom functionality.
    """

    def __init__(self):
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.fmp_key = os.getenv('FINANCIAL_MODELING_PREP_API_KEY')
        self.polygon_key = os.getenv('POLYGON_API_KEY')
        self.finnhub_key = os.getenv('FINNHUB_API_KEY')
        self.twelve_data_key = os.getenv('TWELVE_DATA_API_KEY')

        if not self.alpha_vantage_key:
            logger.warning("ALPHA_VANTAGE_API_KEY not found - Alpha Vantage features will be disabled")
        if not self.fmp_key:
            logger.warning("FINANCIAL_MODELING_PREP_API_KEY not found - Financial Modeling Prep features will be disabled")
        if not self.polygon_key:
            logger.warning("POLYGON_API_KEY not found - Polygon.io features will be disabled")
        if not self.finnhub_key:
            logger.warning("FINNHUB_API_KEY not found - Finnhub features will be disabled")
        if not self.twelve_data_key:
            logger.warning("TWELVE_DATA_API_KEY not found - Twelve Data features will be disabled")

    def get_quarterly_reports(self, symbols: List[str] = None) -> Dict[str, Any]:
        """
        Get quarterly earnings reports and financial statements for peer companies.

        Args:
            symbols: List of stock symbols (e.g., ['AAPL', 'MSFT', 'GOOGL'])

        Returns:
            Dict containing quarterly reports data
        """
        if not symbols:
            symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']  # Default tech peers

        reports = {}

        for symbol in symbols:
            try:
                # Get earnings data from Alpha Vantage
                earnings = self._get_alpha_vantage_earnings(symbol)
                # Get income statement from Alpha Vantage
                income_stmt = self._get_alpha_vantage_income_statement(symbol)

                reports[symbol] = {
                    'earnings': earnings,
                    'income_statement': income_stmt,
                    'last_updated': datetime.now().isoformat()
                }

            except Exception as e:
                logger.error(f"Error fetching quarterly reports for {symbol}: {e}")
                reports[symbol] = {'error': str(e)}

        return {
            'quarterly_reports': reports,
            'data_source': 'Alpha Vantage API',
            'timestamp': datetime.now().isoformat()
        }

    def get_executive_speeches(self, symbols: List[str] = None, quarters: List[str] = None) -> Dict[str, Any]:
        """
        Get earnings call transcripts (executive speeches) for peer companies.

        Args:
            symbols: List of stock symbols
            quarters: List of quarters (e.g., ['2024Q1', '2023Q4'])

        Returns:
            Dict containing executive speech transcripts
        """
        if not symbols:
            symbols = ['AAPL', 'MSFT', 'GOOGL']
        if not quarters:
            # Get last 4 quarters
            now = datetime.now()
            quarters = []
            for i in range(4):
                quarter = ((now.month - 1) // 3) + 1
                year = now.year
                if quarter - i <= 0:
                    year -= 1
                    quarter = 4 + (quarter - i)
                else:
                    quarter -= i
                quarters.append(f"{year}Q{quarter}")

        speeches = {}

        for symbol in symbols:
            symbol_speeches = {}
            for quarter in quarters:
                try:
                    transcript = self._get_alpha_vantage_earnings_transcript(symbol, quarter)
                    if transcript:
                        symbol_speeches[quarter] = transcript
                except Exception as e:
                    logger.error(f"Error fetching transcript for {symbol} {quarter}: {e}")

            if symbol_speeches:
                speeches[symbol] = symbol_speeches

        return {
            'executive_speeches': speeches,
            'data_source': 'Alpha Vantage EARNINGS_CALL_TRANSCRIPT API',
            'timestamp': datetime.now().isoformat()
        }

    def get_capital_markets_updates(self, symbols: List[str] = None) -> Dict[str, Any]:
        """
        Get capital markets updates including press releases, stock news, real-time quotes, and historical data.

        Args:
            symbols: List of stock symbols

        Returns:
            Dict containing capital markets updates
        """
        if not symbols:
            symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']

        updates = {}

        for symbol in symbols:
            try:
                # Get market news from Polygon.io
                news = self._get_polygon_market_news(symbol)
                # Get recent trades/price data from Polygon.io
                trades = self._get_polygon_recent_trades(symbol)
                # Get real-time quote from Twelve Data
                quote = self._get_twelve_data_quote(symbol)
                # Get recent historical data from Twelve Data
                historical = self._get_twelve_data_historical(symbol, interval='1day', outputsize=5)

                updates[symbol] = {
                    'news': news,
                    'recent_trades': trades,
                    'real_time_quote': quote,
                    'recent_historical': historical,
                    'last_updated': datetime.now().isoformat()
                }

            except Exception as e:
                logger.error(f"Error fetching capital markets updates for {symbol}: {e}")
                updates[symbol] = {'error': str(e)}

        return {
            'capital_markets_updates': updates,
            'data_source': 'Polygon.io API + Twelve Data API',
            'timestamp': datetime.now().isoformat()
        }

    def get_peer_analysis(self, symbols: List[str] = None) -> Dict[str, Any]:
        """
        Get comprehensive peer analysis including company profiles and key metrics.

        Args:
            symbols: List of stock symbols

        Returns:
            Dict containing peer analysis data
        """
        if not symbols:
            symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']

        analysis = {}

        for symbol in symbols:
            try:
                # Get company profile from Finnhub
                profile = self._get_finnhub_company_profile(symbol)
                # Get basic financials from Finnhub
                financials = self._get_finnhub_basic_financials(symbol)

                analysis[symbol] = {
                    'company_profile': profile,
                    'basic_financials': financials,
                    'last_updated': datetime.now().isoformat()
                }

            except Exception as e:
                logger.error(f"Error fetching peer analysis for {symbol}: {e}")
                analysis[symbol] = {'error': str(e)}

        return {
            'peer_analysis': analysis,
            'data_source': 'Finnhub API',
            'timestamp': datetime.now().isoformat()
        }

    # Alpha Vantage API methods
    def _get_alpha_vantage_earnings(self, symbol: str) -> Dict[str, Any]:
        """Get earnings data from Alpha Vantage."""
        if not self.alpha_vantage_key:
            raise ValueError("Alpha Vantage API key not configured")

        url = f"https://www.alphavantage.co/query?function=EARNINGS&symbol={symbol}&apikey={self.alpha_vantage_key}"

        response = requests.get(url)
        response.raise_for_status()

        data = response.json()

        if 'quarterlyEarnings' in data:
            # Return last 4 quarters
            return data['quarterlyEarnings'][:4]

        return data

    def _get_alpha_vantage_income_statement(self, symbol: str) -> Dict[str, Any]:
        """Get income statement from Alpha Vantage."""
        if not self.alpha_vantage_key:
            raise ValueError("Alpha Vantage API key not configured")

        url = f"https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={symbol}&apikey={self.alpha_vantage_key}"

        response = requests.get(url)
        response.raise_for_status()

        data = response.json()

        if 'quarterlyReports' in data:
            # Return last 4 quarters
            return data['quarterlyReports'][:4]

        return data

    def _get_alpha_vantage_earnings_transcript(self, symbol: str, quarter: str) -> Optional[Dict[str, Any]]:
        """Get earnings call transcript from Alpha Vantage."""
        if not self.alpha_vantage_key:
            raise ValueError("Alpha Vantage API key not configured")

        url = f"https://www.alphavantage.co/query?function=EARNINGS_CALL_TRANSCRIPT&symbol={symbol}&quarter={quarter}&apikey={self.alpha_vantage_key}"

        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if 'transcript' in data and data['transcript']:
                return data
        else:
            logger.warning(f"No transcript available for {symbol} {quarter}")

        return None

    # Financial Modeling Prep API methods
    def _get_fmp_press_releases(self, symbol: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get press releases from Financial Modeling Prep."""
        if not self.fmp_key:
            raise ValueError("Financial Modeling Prep API key not configured")

        try:
            url = f"https://financialmodelingprep.com/api/v3/press-releases/{symbol}?limit={limit}&apikey={self.fmp_key}"
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 403:
                logger.warning(f"FMP press releases endpoint not available for {symbol} (legacy endpoint): {e}")
                return []  # Return empty list instead of failing
            raise

    def _get_fmp_stock_news(self, symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get stock news from Financial Modeling Prep."""
        if not self.fmp_key:
            raise ValueError("Financial Modeling Prep API key not configured")

        try:
            url = f"https://financialmodelingprep.com/api/v3/stock_news?tickers={symbol}&limit={limit}&apikey={self.fmp_key}"
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 403:
                logger.warning(f"FMP stock news endpoint not available for {symbol} (legacy endpoint): {e}")
                return []  # Return empty list instead of failing
            raise

    def _get_fmp_company_profile(self, symbol: str) -> Dict[str, Any]:
        """Get company profile from Financial Modeling Prep."""
        if not self.fmp_key:
            raise ValueError("Financial Modeling Prep API key not configured")

        try:
            url = f"https://financialmodelingprep.com/api/v3/profile/{symbol}?apikey={self.fmp_key}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return data[0] if data else {}
        except requests.exceptions.HTTPError as e:
            if response.status_code == 403:
                logger.warning(f"FMP company profile endpoint not available for {symbol} (legacy endpoint): {e}")
                return {}  # Return empty dict instead of failing
            raise

    def _get_fmp_key_metrics(self, symbol: str, period: str = 'quarter', limit: int = 4) -> List[Dict[str, Any]]:
        """Get key metrics from Financial Modeling Prep."""
        if not self.fmp_key:
            raise ValueError("Financial Modeling Prep API key not configured")

        try:
            url = f"https://financialmodelingprep.com/api/v3/key-metrics/{symbol}?period={period}&limit={limit}&apikey={self.fmp_key}"
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 403:
                logger.warning(f"FMP key metrics endpoint not available for {symbol} (legacy endpoint): {e}")
                return []  # Return empty list instead of failing
            raise

    # Polygon.io API methods
    def _get_polygon_market_news(self, symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get market news from Polygon.io."""
        if not self.polygon_key:
            raise ValueError("Polygon.io API key not configured")

        try:
            url = f"https://api.polygon.io/v2/reference/news?ticker={symbol}&limit={limit}&apiKey={self.polygon_key}"
            response = requests.get(url)
            response.raise_for_status()

            data = response.json()
            if 'results' in data:
                # Transform to consistent format
                return [{
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'url': article.get('article_url', ''),
                    'publishedDate': article.get('published_utc', ''),
                    'source': article.get('publisher', {}).get('name', 'Polygon.io'),
                    'tickers': article.get('tickers', [])
                } for article in data['results']]

            return []
        except requests.exceptions.HTTPError as e:
            logger.warning(f"Polygon market news not available for {symbol}: {e}")
            return []

    def _get_polygon_recent_trades(self, symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent trades data from Polygon.io."""
        if not self.polygon_key:
            raise ValueError("Polygon.io API key not configured")

        try:
            # Get last trade for the symbol (different endpoint)
            url = f"https://api.polygon.io/v2/last/trade/{symbol}?apiKey={self.polygon_key}"
            response = requests.get(url)
            response.raise_for_status()

            data = response.json()
            if 'results' in data:
                trade = data['results']
                return [{
                    'symbol': symbol,
                    'price': trade.get('price', 0),
                    'size': trade.get('size', 0),
                    'timestamp': trade.get('timestamp', 0),
                    'exchange': trade.get('exchange', 0),
                    'conditions': trade.get('conditions', [])
                }]
            return []
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                logger.warning(f"Polygon recent trades not available for {symbol} (market closed or no data): {e}")
                return []
            logger.warning(f"Polygon recent trades error for {symbol}: {e}")
            return []

    # Finnhub API methods
    def _get_finnhub_company_profile(self, symbol: str) -> Dict[str, Any]:
        """Get company profile from Finnhub."""
        if not self.finnhub_key:
            raise ValueError("Finnhub API key not configured")

        try:
            url = f"https://finnhub.io/api/v1/stock/profile2?symbol={symbol}&token={self.finnhub_key}"
            response = requests.get(url)
            response.raise_for_status()

            data = response.json()
            return data if data else {}
        except requests.exceptions.HTTPError as e:
            logger.warning(f"Finnhub company profile not available for {symbol}: {e}")
            return {}

    def _get_finnhub_basic_financials(self, symbol: str, metric: str = 'all') -> Dict[str, Any]:
        """Get basic financials from Finnhub."""
        if not self.finnhub_key:
            raise ValueError("Finnhub API key not configured")

        try:
            url = f"https://finnhub.io/api/v1/stock/metric?symbol={symbol}&metric={metric}&token={self.finnhub_key}"
            response = requests.get(url)
            response.raise_for_status()

            data = response.json()
            return data.get('metric', {}) if data else {}
        except requests.exceptions.HTTPError as e:
            logger.warning(f"Finnhub basic financials not available for {symbol}: {e}")
            return {}

    # Twelve Data API methods
    def _get_twelve_data_quote(self, symbol: str) -> Dict[str, Any]:
        """Get real-time quote from Twelve Data."""
        if not self.twelve_data_key:
            raise ValueError("Twelve Data API key not configured")

        try:
            url = f"https://api.twelvedata.com/quote?symbol={symbol}&apikey={self.twelve_data_key}"
            response = requests.get(url)
            response.raise_for_status()

            data = response.json()
            return data if data else {}
        except requests.exceptions.HTTPError as e:
            logger.warning(f"Twelve Data quote not available for {symbol}: {e}")
            return {}

    def _get_twelve_data_historical(self, symbol: str, interval: str = '1day', outputsize: int = 30) -> List[Dict[str, Any]]:
        """Get historical data from Twelve Data."""
        if not self.twelve_data_key:
            raise ValueError("Twelve Data API key not configured")

        try:
            url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&outputsize={outputsize}&apikey={self.twelve_data_key}"
            response = requests.get(url)
            response.raise_for_status()

            data = response.json()
            if 'values' in data:
                return data['values']
            return []
        except requests.exceptions.HTTPError as e:
            logger.warning(f"Twelve Data historical data not available for {symbol}: {e}")
            return []

    def _get_twelve_data_technical_indicator(self, symbol: str, indicator: str = 'sma', interval: str = '1day', time_period: int = 20) -> Dict[str, Any]:
        """Get technical indicator from Twelve Data."""
        if not self.twelve_data_key:
            raise ValueError("Twelve Data API key not configured")

        try:
            url = f"https://api.twelvedata.com/{indicator}?symbol={symbol}&interval={interval}&time_period={time_period}&apikey={self.twelve_data_key}"
            response = requests.get(url)
            response.raise_for_status()

            data = response.json()
            return data if data else {}
        except requests.exceptions.HTTPError as e:
            logger.warning(f"Twelve Data technical indicator not available for {symbol}: {e}")
            return {}