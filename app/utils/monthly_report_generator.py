from datetime import datetime, timedelta
from typing import List, Dict
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import aliased
from app import db
from app.models import (
    Customer,
    CustomerStatus,
    Transaction,
    TransactionType,
    TransactionStatus,
    Asset,
    AssetPrice, KYCStatus,
)


def generate_customer_growth_report(start_date: datetime, end_date: datetime) -> Dict:
    """
    Generate report of customer growth by citizenship and customer type.
    This report includes:
    - Starting customers: Customers at the beginning of the period
    - New customers: Customers who joined during the period
    - Exiting customers: Customers who left/deactivated during the period
    - Ending customers: Customers at the end of the period

    Args:
        start_date: Beginning of reporting period
        end_date: End of reporting period

    Returns:
        Dictionary with customer growth data
    """
    # Initialize result structure
    result = {
        "starting_customers": {
            "Asing": {"corporate": 0, "individual": 0},
            "Domestik": {"corporate": 0, "individual": 0}
        },
        "new_customers": {
            "Asing": {"corporate": 0, "individual": 0},
            "Domestik": {"corporate": 0, "individual": 0}
        },
        "exiting_customers": {
            "Asing": {"corporate": 0, "individual": 0},
            "Domestik": {"corporate": 0, "individual": 0}
        },
        "ending_customers": {
            "Asing": {"corporate": 0, "individual": 0},
            "Domestik": {"corporate": 0, "individual": 0}
        }
    }
    # Query to get starting customers
    starting_customers = db.session.query(
        Customer.citizenship,
        Customer.customer_type,
        func.count(Customer.id).label('count')
    ).filter(
        and_(
            func.date(Customer.kyc_approved_at) < start_date.date(),
            or_(
                Customer.status == CustomerStatus.ACTIVE,
                and_(
                    Customer.status == CustomerStatus.DEACTIVATED,
                    func.date(Customer.updated_at) > start_date.date()
                )
            )
        )
    ).group_by(
        Customer.citizenship, Customer.customer_type
    ).all()
    # Process starting customers
    for customer in starting_customers:
        citizenship = customer.citizenship.value
        customer_type = customer.customer_type.value.lower()
        result["starting_customers"][citizenship][customer_type] += customer.count

    # Query to get new customers
    new_customers = db.session.query(
        Customer.citizenship,
        Customer.customer_type,
        func.count(Customer.id).label('count')
    ).filter(
        func.date(Customer.kyc_approved_at) >= start_date.date(),
        func.date(Customer.kyc_approved_at) <= end_date.date(),
    ).group_by(
        Customer.citizenship, Customer.customer_type
    ).all()
    # Process new customers
    for customer in new_customers:
        citizenship = customer.citizenship.value
        customer_type = customer.customer_type.value.lower()
        result["new_customers"][citizenship][customer_type] += customer.count

    # Query to get exiting customers
    exiting_customers = db.session.query(
        Customer.citizenship,
        Customer.customer_type,
        func.count(Customer.id).label('count')
    ).filter(
        Customer.status == CustomerStatus.DEACTIVATED,
        func.date(Customer.updated_at) >= start_date.date(),
        func.date(Customer.updated_at) <= end_date.date()
    ).group_by(
        Customer.citizenship, Customer.customer_type
    ).all()
    # Process exiting customers
    for customer in exiting_customers:
        citizenship = customer.citizenship.value
        customer_type = customer.customer_type.value.lower()
        result["exiting_customers"][citizenship][customer_type] += customer.count

    ending_customers = db.session.query(
        Customer.citizenship,
        Customer.customer_type,
        func.count(Customer.id).label('count')
    ).filter(
        or_(
            and_(Customer.status == CustomerStatus.ACTIVE, func.date(Customer.kyc_approved_at) <= end_date.date()),
            and_(Customer.status == CustomerStatus.DEACTIVATED, func.date(Customer.updated_at) > end_date.date())
        )
    ).group_by(
        Customer.citizenship, Customer.customer_type
    ).all()
    # Process ending customers
    for customer in ending_customers:
        citizenship = customer.citizenship.value
        customer_type = customer.customer_type.value.lower()
        result["ending_customers"][citizenship][customer_type] += customer.count
    return result


def generate_top20_customers_by_transaction_value(start_date: datetime, end_date: datetime) -> List[Dict]:
    """
    Generate report of top 20 customers by transaction value
    This report includes:
    - Customer name
    - Total transaction value

    Args:
        start_date: Beginning of reporting period
        end_date: End of reporting period

    Returns:
        List of dictionaries with customer name and total transaction value
    """
    # Query to get top 20 customers by transaction value
    subquery = db.session.query(
        Transaction.customer_id,
        func.sum(Transaction.amount).label('total_transaction_value')
    ).filter(
        Transaction.transaction_type.in_([TransactionType.BUY, TransactionType.SELL]),
        Transaction.status == TransactionStatus.COMPLETED,
        func.date(Transaction.created_at) >= start_date.date(),
        func.date(Transaction.created_at) <= end_date.date()
    ).group_by(
        Transaction.customer_id
    ).subquery()

    top_customers = db.session.query(
        Customer.identification_type,
        Customer.identification_number,
        Customer.name,
        Customer.citizenship,
        Customer.customer_type,
        subquery.c.total_transaction_value
    ).join(
        subquery, Customer.id == subquery.c.customer_id
    ).order_by(
        subquery.c.total_transaction_value.desc()
    ).limit(20).all()

    # Process top customers
    result = []

    for customer in top_customers:
        customer_type = "Individu " if customer.customer_type.value == "Individual" else "Badan Usaha"
        result.append({
            "customer_type": "Individu " if customer.customer_type.value == "Individual" else "Badan Usaha",
            "identification_type": "NPWP (Domestik)" if customer_type == "Badan Usaha" and customer.identification_type == "NPWP" else "Identification No./ Tax Id/Sejenis (Asing)" if customer_type == "Badan Usaha" else "NIK (Domestik)" if customer.identification_type == "KTP" else "National ID (Asing)",
            "identification_number": customer.identification_number,
            "name": customer.name,
            "citizenship": customer.citizenship.value,
            "total_transaction_value": customer.total_transaction_value
        })
    return result


def generate_top20_customers_by_withdrawal_value(start_date: datetime, end_date: datetime) -> List[Dict]:
    """
    Generate report of top 20 customers by withdrawal value
    This report includes:
    - Customer name
    - Total withdrawal value

    Args:
        start_date: Beginning of reporting period
        end_date: End of reporting period

    Returns:
        List of dictionaries with customer name and total withdrawal value
    """
    subquery = db.session.query(
        Transaction.customer_id,
        func.sum(Transaction.amount).label('total_transaction_value')
    ).filter(
        Transaction.transaction_type.in_([TransactionType.WITHDRAWAL]),
        Transaction.status == TransactionStatus.COMPLETED,
        func.date(Transaction.created_at) >= start_date.date(),
        func.date(Transaction.created_at) <= end_date.date()
    ).group_by(
        Transaction.customer_id
    ).subquery()

    top_customers = db.session.query(
        Customer.identification_type,
        Customer.identification_number,
        Customer.name,
        Customer.citizenship,
        Customer.customer_type,
        subquery.c.total_transaction_value
    ).join(
        subquery, Customer.id == subquery.c.customer_id
    ).order_by(
        subquery.c.total_transaction_value.desc()
    ).limit(20).all()

    # Process top customers
    result = []
    for customer in top_customers:
        customer_type = "Individu " if customer.customer_type.value == "Individual" else "Badan Usaha"
        result.append({
            "customer_type": "Individu " if customer.customer_type.value == "Individual" else "Badan Usaha",
            "identification_type": "NPWP (Domestik)" if customer_type == "Badan Usaha" and customer.identification_type == "NPWP" else "Identification No./ Tax Id/Sejenis (Asing)" if customer_type == "Badan Usaha" else "NIK (Domestik)" if customer.identification_type == "KTP" else "National ID (Asing)",
            "identification_number": customer.identification_number,
            "name": customer.name,
            "citizenship": customer.citizenship.value,
            "total_transaction_value": customer.total_transaction_value
        })
    return result


def generate_top20_customers_by_topup_value(start_date: datetime, end_date: datetime) -> List[Dict]:
    """
    Generate report of top 20 customers by topup value
    This report includes:
    - Customer name
    - Total topup value

    Args:
        start_date: Beginning of reporting period
        end_date: End of reporting period

    Returns:
        List of dictionaries with customer name and total topup value
    """
    subquery = db.session.query(
        Transaction.customer_id,
        func.sum(Transaction.amount).label('total_transaction_value')
    ).filter(
        Transaction.transaction_type.in_([TransactionType.DEPOSIT]),
        Transaction.status == TransactionStatus.COMPLETED,
        func.date(Transaction.created_at) >= start_date.date(),
        func.date(Transaction.created_at) <= end_date.date()
    ).group_by(
        Transaction.customer_id
    ).subquery()

    top_customers = db.session.query(
        Customer.identification_type,
        Customer.identification_number,
        Customer.name,
        Customer.citizenship,
        Customer.customer_type,
        subquery.c.total_transaction_value
    ).join(
        subquery, Customer.id == subquery.c.customer_id
    ).order_by(
        subquery.c.total_transaction_value.desc()
    ).limit(20).all()

    # Process top customers
    result = []
    for customer in top_customers:
        customer_type = "Individu " if customer.customer_type.value == "Individual" else "Badan Usaha"
        result.append({
            "customer_type": "Individu " if customer.customer_type.value == "Individual" else "Badan Usaha",
            "identification_type": "NPWP (Domestik)" if customer_type == "Badan Usaha" and customer.identification_type == "NPWP" else "Identification No./ Tax Id/Sejenis (Asing)" if customer_type == "Badan Usaha" else "NIK (Domestik)" if customer.identification_type == "KTP" else "National ID (Asing)",
            "identification_number": customer.identification_number,
            "name": customer.name,
            "citizenship": customer.citizenship.value,
            "total_transaction_value": customer.total_transaction_value
        })
    return result
