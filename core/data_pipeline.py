"""Async data pipeline for bank API integration and ingestion"""
import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import aiohttp
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


@dataclass
class Transaction:
    id: str
    user_id: str
    amount: float
    currency: str
    merchant: str
    description: str
    transaction_date: datetime
    category: Optional[str] = None
    merchant_category_code: Optional[str] = None


class BankAPIConnector(ABC):
    """Abstract base for bank API connectors"""
    
    @abstractmethod
    async def authenticate(self) -> bool:
        pass
    
    @abstractmethod
    async def fetch_transactions(self, days_back: int = 90) -> List[Transaction]:
        pass


class PlaidConnector(BankAPIConnector):
    """Plaid API connector for transaction fetching"""
    
    def __init__(self, client_id: str, secret: str, access_token: str):
        self.client_id = client_id
        self.secret = secret
        self.access_token = access_token
        self.base_url = "https://sandbox.plaid.com"
        self.authenticated = False
        logger.info("PlaidConnector initialized")
    
    async def authenticate(self) -> bool:
        """Authenticate with Plaid API"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/auth/get",
                    json={"client_id": self.client_id, "secret": self.secret, "access_token": self.access_token}
                ) as resp:
                    if resp.status == 200:
                        self.authenticated = True
                        logger.info("Plaid authentication successful")
                        return True
        except Exception as e:
            logger.error(f"Plaid authentication failed: {e}")
        return False
    
    async def fetch_transactions(self, days_back: int = 90) -> List[Transaction]:
        """Fetch transactions from Plaid"""
        if not self.authenticated:
            await self.authenticate()
        
        transactions = []
        start_date = (datetime.now() - timedelta(days=days_back)).date().isoformat()
        end_date = datetime.now().date().isoformat()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/transactions/get",
                    json={
                        "client_id": self.client_id,
                        "secret": self.secret,
                        "access_token": self.access_token,
                        "start_date": start_date,
                        "end_date": end_date
                    }
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        for txn in data.get("transactions", []):
                            transactions.append(Transaction(
                                id=txn["transaction_id"],
                                user_id="plaid_user",
                                amount=abs(txn["amount"]),
                                currency=txn["iso_currency_code"],
                                merchant=txn.get("merchant_name", "Unknown"),
                                description=txn.get("name", ""),
                                transaction_date=datetime.fromisoformat(txn["date"]),
                                merchant_category_code=txn.get("personal_finance_category")
                            ))
        except Exception as e:
            logger.error(f"Plaid transaction fetch failed: {e}")
        
        return transactions


class DataPipeline:
    """Main data ingestion and processing pipeline"""
    
    def __init__(self, connectors: List[BankAPIConnector]):
        self.connectors = connectors
        self.batch_size = 100
        self.max_retries = 3
        logger.info(f"DataPipeline initialized with {len(connectors)} connectors")
    
    async def ingest_all_transactions(self, days_back: int = 90) -> List[Transaction]:
        """Fetch transactions from all connectors"""
        all_transactions = []
        tasks = [
            connector.fetch_transactions(days_back)
            for connector in self.connectors
        ]
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Error fetching transactions: {result}")
                else:
                    all_transactions.extend(result)
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
        
        logger.info(f"Ingested {len(all_transactions)} transactions")
        return all_transactions
    
    async def process_batch(self, transactions: List[Transaction]) -> List[Dict[str, Any]]:
        """Process transactions in batches"""
        processed = []
        for i in range(0, len(transactions), self.batch_size):
            batch = transactions[i:i+self.batch_size]
            for txn in batch:
                processed.append({
                    "id": txn.id,
                    "user_id": txn.user_id,
                    "amount": txn.amount,
                    "merchant": txn.merchant,
                    "description": txn.description,
                    "date": txn.transaction_date.isoformat(),
                    "ingested_at": datetime.now().isoformat()
                })
        
        return processed
