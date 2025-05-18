from datetime import datetime, timedelta
from typing import List, Dict
from sqlalchemy import func, case
from sqlalchemy.orm import aliased
from app import db
from app.models import (
    BuySellTransaction,
    DepositWithdrawalTransaction,
    Transaction,
    Asset,
    TransactionStatus,
    TransactionType,
    AssetPrice,
    Customer,
    Citizenship
)


def generate_transactions_by_type_report(start_date: datetime, end_date: datetime) -> Dict:
    """
    Generate report of transactions by customer type and citizenship.

    Args:
        start_date: Beginning of reporting period
        end_date: End of reporting period

    Returns:
        Dictionary with transaction totals organized by citizenship, customer type, and transaction type
    """
    # Initialize result structure
    result = {
        "Asing": {
            "corporate": {"buy": 0, "sell": 0},
            "individual": {"buy": 0, "sell": 0}
        },
        "Domestik": {
            "corporate": {"buy": 0, "sell": 0},
            "individual": {"buy": 0, "sell": 0}
        }
    }

    # Query transactions by type
    transactions_by_type = db.session.query(
        Customer.customer_type,
        Customer.citizenship,
        Transaction.transaction_type,
        func.sum(Transaction.amount).label('total_amount')
    ).join(
        Transaction, Transaction.customer_id == Customer.id
    ).join(
        BuySellTransaction, BuySellTransaction.transaction_id == Transaction.id
    ).filter(
        Transaction.transaction_type.in_([TransactionType.BUY, TransactionType.SELL]),
        Transaction.status == TransactionStatus.COMPLETED,
        Transaction.created_at.between(start_date, end_date)
    ).group_by(
        Customer.customer_type, Customer.citizenship, Transaction.transaction_type
    ).all()

    # Process query results
    for transaction in transactions_by_type:
        customer_type = transaction.customer_type.value.lower()
        citizenship = transaction.citizenship.value
        transaction_type = transaction.transaction_type.lower()
        total_amount = transaction.total_amount

        # Map corporate/individual to appropriate category
        customer_category = "corporate" if customer_type == "corporate" else "individual"

        # Update result dictionary
        result[citizenship][customer_category][transaction_type] += total_amount

    return result


def generate_asset_transaction_report(start_date: datetime, end_date: datetime) -> List[Dict]:
    """
    Generate report of asset transactions within the specified date range.

    Args:
        start_date: Beginning of reporting period
        end_date: End of reporting period

    Returns:
        List of dictionaries containing asset transaction statistics
    """
    lrtak_query = db.session.query(
        Asset.symbol,
        Asset.name,
        func.min(AssetPrice.price).label('min_price'),
        func.max(AssetPrice.price).label('max_price'),
        func.count().label('transaction_frequency'),
        func.sum(Transaction.amount).label('total_volume'),
        func.sum(Transaction.amount * AssetPrice.price).label('total_value')
    ).join(
        BuySellTransaction, BuySellTransaction.transaction_id == Transaction.id
    ).join(
        Asset, Asset.id == BuySellTransaction.asset_id
    ).join(
        AssetPrice, AssetPrice.id == BuySellTransaction.asset_price_id
    ).filter(
        Transaction.status == TransactionStatus.COMPLETED,
        Transaction.transaction_type.in_([TransactionType.BUY, TransactionType.SELL]),
        Transaction.created_at.between(start_date, end_date)
    ).group_by(
        Asset.symbol, Asset.name
    ).order_by(
        func.sum(Transaction.amount * AssetPrice.price).desc()
    ).all()

    # Convert SQLAlchemy results to dictionaries for template rendering
    return [
        {
            'symbol': row.symbol,
            'name': row.name,
            'min_price': row.min_price,
            'max_price': row.max_price,
            'transaction_frequency': row.transaction_frequency,
            'total_volume': row.total_volume,
            'total_value': row.total_value
        }
        for row in lrtak_query
    ]


def generate_holdings_report(cutoff_date: datetime) -> List[Dict]:
    """
    Generate holdings report up to the specified cutoff date.

    Args:
        cutoff_date: Date up to which holdings are calculated

    Returns:
        List of dictionaries with holdings data sorted by price
    """
    # Constants for business logic calculations
    TRADING_CUSTOMER_RATIO = 0.3
    STORAGE_CUSTOMER_RATIO = 0.7

    # Query asset holdings
    holdings_query = db.session.query(
        Asset.id,
        Asset.symbol,
        Asset.name,
        (func.sum(
            case(
                (Transaction.transaction_type == TransactionType.BUY, Transaction.amount),
                else_=-Transaction.amount
            )
        ) * TRADING_CUSTOMER_RATIO).label("akd_konsumen_pedagang"),
        (func.sum(
            case(
                (Transaction.transaction_type == TransactionType.BUY, Transaction.amount),
                else_=-Transaction.amount
            )
        ) * STORAGE_CUSTOMER_RATIO).label("akd_konsumen_penyimpanan")
    ).join(
        BuySellTransaction, BuySellTransaction.asset_id == Asset.id
    ).join(
        Transaction, Transaction.id == BuySellTransaction.transaction_id
    ).filter(
        Transaction.status == TransactionStatus.COMPLETED,
        Transaction.transaction_type.in_([TransactionType.BUY, TransactionType.SELL]),
        Transaction.created_at <= cutoff_date
    ).group_by(
        Asset.id, Asset.symbol, Asset.name
    ).having(
        func.sum(case(
            (Transaction.transaction_type == TransactionType.BUY, Transaction.amount),
            else_=-Transaction.amount
        )) > 0
    ).all()

    # Process results and fetch latest prices
    result = []
    for row in holdings_query:
        # Get latest price for this asset
        latest_price = db.session.query(AssetPrice).filter(
            AssetPrice.asset_id == row.id,
            AssetPrice.price_date <= cutoff_date
        ).order_by(AssetPrice.price_date.desc()).first()

        price = latest_price.price if latest_price else 0

        result.append({
            'symbol': row.symbol,
            'name': row.name,
            'akd_konsumen_pedagang': row.akd_konsumen_pedagang,
            'akd_konsumen_penyimpanan': row.akd_konsumen_penyimpanan,
            'price': price
        })

    # Sort by price in descending order
    return sorted(result, key=lambda x: x['price'], reverse=True)


def generate_topup_withdrawal_report(report_date: datetime) -> List[Dict]:
    """
    Generate a report of topup and withdrawal transactions for a specific date,
    divided into two sessions (00:00-11:59 and 12:00-23:59).

    The report includes wallet snapshots showing balance at the beginning and end of each session,
    along with total topup and withdrawal amounts during each session.

    Args:
        report_date: The date for which to generate the report

    Returns:
        List of dictionaries containing session data with previous balance, topup amount,
        withdrawal amount, and final balance
    """
    # Define session time boundaries
    start_of_day = datetime.combine(report_date.date(), datetime.min.time())
    mid_day = datetime.combine(report_date.date(), datetime.strptime("12:00:00", "%H:%M:%S").time())
    end_of_day = datetime.combine(report_date.date(), datetime.strptime("23:59:59", "%H:%M:%S").time())

    # Get the previous day's final balance
    previous_day = start_of_day - timedelta(days=1)
    previous_day_end = datetime.combine(previous_day.date(), datetime.strptime("23:59:59", "%H:%M:%S").time())

    # Query for the final balance as of the end of the previous day
    previous_day_balance = db.session.query(
        func.sum(case(
            (Transaction.transaction_type == TransactionType.DEPOSIT, Transaction.amount),
            (Transaction.transaction_type == TransactionType.WITHDRAWAL, -Transaction.amount),
            else_=0
        ))
    ).join(
        DepositWithdrawalTransaction, DepositWithdrawalTransaction.transaction_id == Transaction.id
    ).filter(
        Transaction.status == TransactionStatus.COMPLETED,
        Transaction.transaction_type.in_([TransactionType.DEPOSIT, TransactionType.WITHDRAWAL]),
        Transaction.created_at <= previous_day_end
    ).scalar() or 0

    # Initialize result list
    result = []

    # Define the two sessions
    sessions = [
        {"id": 1, "start": start_of_day, "end": mid_day - timedelta(seconds=1)},
        {"id": 2, "start": mid_day, "end": end_of_day}
    ]

    current_balance = previous_day_balance

    # Process each session
    for session in sessions:
        # Query for topup and withdrawal amounts in this session
        session_transactions = db.session.query(
            Transaction.transaction_type,
            func.sum(Transaction.amount).label('total_amount')
        ).join(
            DepositWithdrawalTransaction, DepositWithdrawalTransaction.transaction_id == Transaction.id
        ).filter(
            Transaction.status == TransactionStatus.COMPLETED,
            Transaction.transaction_type.in_([TransactionType.DEPOSIT, TransactionType.WITHDRAWAL]),
            Transaction.created_at.between(session["start"], session["end"])
        ).group_by(
            Transaction.transaction_type
        ).all()

        # Initialize topup and withdrawal amounts
        topup_amount = 0
        withdrawal_amount = 0

        # Process transaction totals
        for transaction in session_transactions:
            if transaction.transaction_type == TransactionType.DEPOSIT:
                topup_amount = transaction.total_amount
            elif transaction.transaction_type == TransactionType.WITHDRAWAL:
                withdrawal_amount = transaction.total_amount

        # Calculate final balance for this session
        previous_balance = current_balance
        final_balance = previous_balance + topup_amount - withdrawal_amount
        current_balance = final_balance

        # Add session data to result
        result.append({
            'session': session["id"],
            'previous_balance': previous_balance,
            'topup': topup_amount,
            'withdrawal': withdrawal_amount,
            'final_balance': final_balance
        })

    return result
