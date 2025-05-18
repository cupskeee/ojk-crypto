# app/reporting/daily.py
from app import db
from app.models import Asset, BuySellTransaction, Transaction, AssetPrice, TransactionStatus, TransactionType
from sqlalchemy import func

def get_lrtak_data(start_date, end_date):
    lrtak = db.session.query(
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
        func.count().desc()
    ).all()

    return lrtak