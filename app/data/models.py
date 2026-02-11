"""
Data models for Market Data page.
"""
from dataclasses import dataclass
from datetime import date
from typing import Optional, List


@dataclass
class Company:
    """Company model from coreiq_companies table."""
    ticker: str
    name: str
    name_coresight: Optional[str]
    exchange: Optional[str]
    
    @property
    def display_name(self) -> str:
        """Format: 'Macy's Inc. (NYSE:M)'"""
        name = self.name_coresight or self.name
        exchange = self.exchange or ""
        return f"{name} ({exchange}:{self.ticker})"


@dataclass
class IncomeStatementLineItem:
    """Income statement line item for display."""
    label: str
    key: str  # Database column name
    values: List[Optional[float]]  # Values for each period
    is_calculated: bool = False


@dataclass
class FiscalPeriod:
    """Fiscal period for column headers."""
    date: date
    label: str
    
    @classmethod
    def from_date(cls, dt: date) -> "FiscalPeriod":
        """Create from date: '12 Months\nJan-29-2021'"""
        return cls(
            date=dt,
            label=f"12 Months\n{dt.strftime('%b-%d-%Y')}"
        )


@dataclass
class IncomeStatementData:
    """Complete income statement data for a company."""
    company: Company
    periods: List[FiscalPeriod]
    line_items: List[IncomeStatementLineItem]
