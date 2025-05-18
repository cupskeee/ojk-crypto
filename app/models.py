import enum
from app import db, bcrypt
from flask_login import UserMixin


class Citizenship(enum.Enum):
    WNI = 'Domestik'
    WNA = 'Asing'

    def __str__(self):
        return self.value

    @classmethod
    def choices(cls):
        return [(choice.name, choice.value) for choice in cls]


class TransactionType(enum.Enum):
    DEPOSIT = 'Deposit'
    WITHDRAWAL = 'Withdrawal'
    BUY = 'Buy'
    SELL = 'Sell'

    def __str__(self):
        return self.value

    def lower(self):
        return self.value.lower()

    @classmethod
    def choices(cls):
        return [(choice.name, choice.value) for choice in cls]


class TransactionStatus(enum.Enum):
    PENDING = 'Pending'
    COMPLETED = 'Completed'
    FAILED = 'Failed'

    def __str__(self):
        return self.value

    @classmethod
    def choices(cls):
        return [(choice.name, choice.value) for choice in cls]

class CustomerStatus(enum.Enum):
    ACTIVE = 'Active'
    DEACTIVATED = 'Deactivated'

    def __str__(self):
        return self.value

    @classmethod
    def choices(cls):
        return [(choice.name, choice.value) for choice in cls]

class KYCStatus(enum.Enum):
    PENDING = 'Pending'
    APPROVED = 'Approved'
    REJECTED = 'Rejected'

    def __str__(self):
        return self.value

    @classmethod
    def choices(cls):
        return [(choice.name, choice.value) for choice in cls]


class IdentificationType(enum.Enum):
    KTP = 'KTP'
    SIM = 'SIM'
    PASSPORT = 'PASSPORT'
    KITAS = 'KITAS'
    KITAP = 'KITAP'
    NPWP = 'NPWP'

    def __str__(self):
        return self.value

    @classmethod
    def choices(cls):
        return [(choice.name, choice.value) for choice in cls]


class CustomerType(enum.Enum):
    INDIVIDUAL = 'Individual'
    CORPORATE = 'Corporate'

    def __str__(self):
        return self.value

    @classmethod
    def choices(cls):
        return [(choice.name, choice.value) for choice in cls]


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def __str__(self):
        return f'User {self.username}'

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        try:
            return bcrypt.check_password_hash(self.password_hash, password)
        except ValueError:
            return False


class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), nullable=False)
    citizenship = db.Column(db.Enum(Citizenship), nullable=False)
    identification_type = db.Column(db.Enum(IdentificationType), nullable=False)
    identification_number = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    domicile = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    kyc_status = db.Column(db.Enum(KYCStatus), default=KYCStatus.PENDING)
    status = db.Column(db.Enum(CustomerStatus), default=CustomerStatus.ACTIVE, nullable=False)
    kyc_approved_at = db.Column(db.DateTime, nullable=True)
    customer_type = db.Column(db.Enum(CustomerType), nullable=False, default=CustomerType.INDIVIDUAL)

    def __str__(self):
        return f'Customer {self.name}'


class Asset(db.Model):
    __tablename__ = 'assets'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), nullable=False)
    symbol = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def price(self):
        latest_price = (db.session.query(AssetPrice)
                        .filter_by(asset_id=self.id)
                        .order_by(AssetPrice.price_date.desc())
                        .first())
        return latest_price.price if latest_price else None

    def __str__(self):
        return f'Asset {self.id}'


class AssetPrice(db.Model):
    __tablename__ = 'asset_prices'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    price = db.Column(db.Float, nullable=False)
    price_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    asset = db.relationship('Asset', backref='prices')

    def __str__(self):
        return f'AssetPrice {self.id}'


class Wallet(db.Model):
    # Represents a wallet for a customer monetary balance
    __tablename__ = 'wallets'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    balance = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    customer = db.relationship('Customer', backref='wallets')

    def __str__(self):
        return f'Wallet {self.id}'


class Holding(db.Model):
    # Represents a holding of an asset for a customer
    __tablename__ = 'holdings'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quantity = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    asset = db.relationship('Asset', backref='holdings')
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    customer = db.relationship('Customer', backref='holdings')

    def __str__(self):
        return f'Holding {self.id}'

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    transaction_type = db.Column(db.Enum(TransactionType), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.Enum(TransactionStatus), default=TransactionStatus.PENDING)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    customer = db.relationship('Customer', backref='transactions')

    def __str__(self):
        return f'Transaction {self.id}'

class DepositWithdrawalTransaction(db.Model):
    __tablename__ = 'deposit_withdrawal_transactions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id'), nullable=False)
    transaction = db.relationship('Transaction', backref='deposit_withdrawal_transactions')
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.id'), nullable=False)
    wallet = db.relationship('Wallet', backref='deposit_withdrawal_transactions')

    def __str__(self):
        return f'DepositWithdrawalTransaction {self.id}'

class BuySellTransaction(db.Model):
    __tablename__ = 'buy_sell_transactions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    asset = db.relationship('Asset', backref='buy_sell_transactions')
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id'), nullable=False)
    transaction = db.relationship('Transaction', backref='buy_sell_transactions')
    asset_price_id = db.Column(db.Integer, db.ForeignKey('asset_prices.id'), nullable=False)
    asset_price = db.relationship('AssetPrice', backref='buy_sell_transactions')

    def __str__(self):
        return f'BuySellTransaction {self.id}'

class Settings(db.Model):
    __tablename__ = 'settings'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.String(150), unique=True, nullable=False)
    value = db.Column(db.String(255), nullable=False)

    def __str__(self):
        return f'Setting {self.key}'