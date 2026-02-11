"""
Data repository for fetching market data from database.
"""
from typing import List, Optional, Tuple
from datetime import date

from core.database import db_manager
from data.models import Company, IncomeStatementLineItem, FiscalPeriod, IncomeStatementData


class CompanyRepository:
    """Repository for coreiq_companies table."""
    
    @staticmethod
    def get_all_sources() -> List[str]:
        """Get distinct data sources."""
        query = "SELECT DISTINCT source FROM coreiq_companies WHERE source IS NOT NULL ORDER BY source"
        results = db_manager.execute_query(query)
        return [row['source'] for row in results if row['source']]
    
    @staticmethod
    def get_companies_by_source() -> List[Company]:
        """Get all companies for a data source."""
        query = """
            SELECT ticker, name, name_coresight, exchange
            FROM coreiq_companies
            WHERE source = 'SEC'
            ORDER BY name_coresight, name
        """
        results = db_manager.execute_query(query)
        return [Company(
            ticker=row['ticker'],
            name=row['name'],
            name_coresight=row['name_coresight'],
            exchange=row['exchange'],
        ) for row in results]
    
    @staticmethod
    def get_company_by_ticker(ticker: str) -> Optional[Company]:
        """Get single company by ticker."""
        query = """
            SELECT ticker, name, name_coresight, exchange, source
            FROM coreiq_companies
            WHERE ticker = :ticker
            LIMIT 1
        """
        results = db_manager.execute_query(query, {"ticker": ticker})
        if not results:
            return None
        row = results[0]
        return Company(
            ticker=row['ticker'],
            name=row['name'],
            name_coresight=row['name_coresight'],
            exchange=row['exchange'],
        )


class IncomeStatementRepository:
    """Repository for coreiq_av_financials_income_statement table."""
    
    # Mapping of UI labels to database columns
    LINE_ITEMS = [
        ("Revenue", "total_revenue", False),
        ("Other Revenue", None, True),  # Will calculate or show "-"
        ("Total Revenue", "total_revenue", False),
        ("Cost Of Goods Sold", "cost_of_revenue", False),
        ("Gross Profit", "gross_profit", False),
        ("Selling General & Admin Exp.", "selling_general_and_administrative", False),
        ("R&D Exp.", "research_and_development", False),
        ("Depreciation & Amort.", "depreciation_and_amortization", False),
        ("Other Operating Expense/(Income)", "other_non_operating_income", False),
        ("Other Operating Exp., Total", "operating_expenses", False),
        ("Operating Income", "operating_income", False),
        ("Interest Expense", "interest_expense", False),
        ("Interest and Invest. Income", "interest_income", False),
        ("Net Interest Exp.", "net_interest_income", False),
    ]
    
    @staticmethod
    def get_date_range(ticker: str) -> Tuple[Optional[date], Optional[date]]:
        """Get min and max fiscal dates for a ticker."""
        query = """
            SELECT 
                MIN(fiscal_date_ending) as min_date,
                MAX(fiscal_date_ending) as max_date
            FROM coreiq_av_financials_income_statement
            WHERE ticker = :ticker
              AND report_type = 'annual'
        """
        results = db_manager.execute_query(query, {"ticker": ticker})
        if not results:
            return None, None
        row = results[0]
        return row['min_date'], row['max_date']
    
    @staticmethod
    def get_available_dates(ticker: str) -> List[date]:
        """Get all available fiscal dates for dropdown."""
        query = """
            SELECT DISTINCT fiscal_date_ending
            FROM coreiq_av_financials_income_statement
            WHERE ticker = :ticker
              AND report_type = 'annual'
            ORDER BY fiscal_date_ending ASC
        """
        results = db_manager.execute_query(query, {"ticker": ticker})
        return [row['fiscal_date_ending'] for row in results]
    
    @staticmethod
    def get_income_statement_data(
        ticker: str,
        start_date: date,
        end_date: date
    ) -> IncomeStatementData:
        """Get income statement data for date range."""
        # Fetch company info
        company = CompanyRepository.get_company_by_ticker(ticker)
        if not company:
            raise ValueError(f"Company not found: {ticker}")
        
        # Fetch raw data
        query = """
            SELECT *
            FROM coreiq_av_financials_income_statement
            WHERE ticker = :ticker
              AND fiscal_date_ending BETWEEN :start_date AND :end_date
              AND report_type = 'annual'
            ORDER BY fiscal_date_ending ASC
        """
        results = db_manager.execute_query(query, {
            "ticker": ticker,
            "start_date": start_date,
            "end_date": end_date
        })
        
        if not results:
            # Return empty structure
            return IncomeStatementData(
                company=company,
                periods=[],
                line_items=[]
            )
        
        # Create periods from results
        periods = [
            FiscalPeriod.from_date(row['fiscal_date_ending'])
            for row in results
        ]
        
        # Build line items
        line_items = []
        for label, column, is_calc in IncomeStatementRepository.LINE_ITEMS:
            values = []
            for row in results:
                if column and row.get(column) is not None:
                    # Convert to millions
                    values.append(float(row[column]) / 1_000_000)
                else:
                    values.append(None)
            
            line_items.append(IncomeStatementLineItem(
                label=label,
                key=column or label,
                values=values,
                is_calculated=is_calc
            ))
        
        return IncomeStatementData(
            company=company,
            periods=periods,
            line_items=line_items
        )
