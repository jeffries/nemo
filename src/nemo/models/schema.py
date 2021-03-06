"""Defines the schema for nemo's backend database."""

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    LargeBinary,
    String
)
from sqlalchemy.orm import relationship

from nemo.models.db import BASE
from nemo.models import magic_numbers

class Currency(BASE): # pylint: disable=too-few-public-methods
    """SQLAlchemy class for currenencies"""

    __tablename__ = magic_numbers.CURRENCY_TABLE

    iso4217_code = Column(String(3), primary_key=True)
    title = Column(String)
    symbol = Column(String(1))
    long_symbol = Column(String(3))
    display_factor = Column(Integer)

    accounts = relationship('Account', back_populates='currency')

class Account(BASE): # pylint: disable=too-few-public-methods
    """SQLAlchemy class for accounts (either personal or institutional)"""

    __tablename__ = magic_numbers.ACCOUNT_TABLE

    id = Column(Integer, primary_key=True) # pylint: disable=invalid-name
    currency_code = Column(String(3), ForeignKey('currencies.iso4217_code'))
    type = Column(String(255))

    currency = relationship('Currency', back_populates='accounts')
    transactions = relationship('AccountTransaction', back_populates='account')

    __mapper_args__ = {
        'polymorphic_identity': magic_numbers.ACCOUNT_POLYID,
        'polymorphic_on': type
    }

class InstitutionAccount(Account): # pylint: disable=too-few-public-methods
    """SQLAlchemy class for institutional (bank) accounts"""

    __tablename__ = magic_numbers.INSTITUTION_ACCOUNT_TABLE

    id = Column(Integer, ForeignKey('accounts.id'), primary_key=True) # pylint: disable=invalid-name
    title = Column(String(255))
    number_suffix = Column(String(4))
    institution_title = Column(String(255))
    minimum_value = Column(Integer)

    __mapper_args__ = {
        'polymorphic_identity': magic_numbers.INSTITUTION_ACCOUNT_POLYID
    }

class PersonalAccount(Account): # pylint: disable=too-few-public-methods
    """SQLAlchemy class for personal accounts"""

    __tablename__ = magic_numbers.PERSONAL_ACCOUNT_TABLE

    id = Column(Integer, ForeignKey('accounts.id'), primary_key=True) # pylint: disable=invalid-name
    holder = Column(String(255))

    __mapper_args__ = {
        'polymorphic_identity': magic_numbers.PERSONAL_ACCOUNT_POLYID
    }

class TransactionCategory(BASE): # pylint: disable=too-few-public-methods
    """SQLAlchemy class for a category of transaction"""

    __tablename__ = magic_numbers.TRANSACTION_CATEGORY_TABLE

    id = Column(Integer, primary_key=True) # pylint: disable=invalid-name
    title = Column(String(255))
    parent_id = Column(
        Integer,
        ForeignKey('{}.id'.format(magic_numbers.TRANSACTION_CATEGORY_TABLE))
    )

    parent = relationship('TransactionCategory', back_populates='children', remote_side=[id])
    children = relationship('TransactionCategory', back_populates='parent')

    categorizations = relationship('TransactionCategorization', back_populates='category')

class AccountTransaction(BASE): # pylint: disable=too-few-public-methods
    """SQLAlchemy class for transactions on accounts"""

    __tablename__ = magic_numbers.ACCOUNT_TRANSACTION_TABLE

    id = Column(Integer, primary_key=True) # pylint: disable=invalid-name
    account_id = Column(
        Integer,
        ForeignKey('{}.id'.format(magic_numbers.ACCOUNT_TABLE))
    )
    title = Column(String(255))
    transaction_date = Column(Date)
    posting_date = Column(Date)
    merchant = Column(String(255))
    transaction_amount = Column(Integer)
    gain_or_loss = Column(Integer)
    instrument = Column(String(255))
    transaction_description = Column(String)
    adjustment_description = Column(String)

    account = relationship('Account', back_populates='transactions')
    categorizations = relationship('TransactionCategorization', back_populates='transaction')
    receipts = relationship('Receipt', back_populates='transaction')

class TransactionAdjustment(BASE): # pylint: disable=too-few-public-methods
    """SQLAlchemy class for an adjustment, linking two transactions"""

    __tablename__ = magic_numbers.TRANSACTION_ADJUSTMENT_TABLE

    id = Column(Integer, primary_key=True) # pylint: disable=invalid-name
    source_transaction_id = Column(
        Integer,
        ForeignKey('{}.id'.format(magic_numbers.ACCOUNT_TRANSACTION_TABLE))
    )
    destination_transaction_id = Column(
        Integer,
        ForeignKey('{}.id'.format(magic_numbers.ACCOUNT_TRANSACTION_TABLE))
    )
    title = Column(String(255))
    notes = Column(String)
    type = Column(String(255))

    source_transaction = relationship(
        'AccountTransaction',
        foreign_keys=[source_transaction_id],
        backref='source_adjustments'
    )
    destination_transaction = relationship(
        'AccountTransaction',
        foreign_keys=[destination_transaction_id],
        backref='destination_adjustments'
    )

    __mapper_args__ = {
        'polymorphic_identity': magic_numbers.TRANSACTION_ADJUSTMENT_POLYID,
        'polymorphic_on': type
    }

class AccountTransactionAdjustment(TransactionAdjustment): # pylint: disable=too-few-public-methods
    """SQLAlchemy class for adjustments linking two transactions in the same currency"""

    __tablename__ = magic_numbers.ACCOUNT_TRANSACTION_ADJUSTMENT_TABLE

    id = Column( # pylint: disable=invalid-name
        Integer,
        ForeignKey('{}.id'.format(magic_numbers.TRANSACTION_ADJUSTMENT_TABLE)),
        primary_key=True
    )
    amount = Column(Integer)

    __mapper_args__ = {
        'polymorphic_identity': magic_numbers.ACCOUNT_TRANSACTION_ADJUSTMENT_POLYID
    }

class CurrencyConversionAdjustment(TransactionAdjustment): # pylint: disable=too-few-public-methods
    """SQLAlchemy class for adjustments linking transactions in different currencies"""

    __tablename__ = magic_numbers.CURRENCY_CONVERSION_ADJUSTMENT_TABLE

    id = Column( # pylint: disable=invalid-name
        Integer,
        ForeignKey('{}.id'.format(magic_numbers.TRANSACTION_ADJUSTMENT_TABLE)),
        primary_key=True
    )
    source_amount = Column(Integer)
    destination_amount = Column(Integer)

    __mapper_args__ = {
        'polymorphic_identity': magic_numbers.CURRENCY_CONVERSION_ADJUSTMENT_POLYID
    }

class TransactionCategorization(BASE): # pylint: disable=too-few-public-methods
    """SQLAlchemy for associating a portion of a transaction with a category"""

    __tablename__ = magic_numbers.TRANSACTION_CATEGORIZATION_TABLE

    transaction_id = Column(
        Integer,
        ForeignKey('{}.id'.format(magic_numbers.ACCOUNT_TRANSACTION_TABLE)),
        primary_key=True
    )
    category_id = Column(
        Integer,
        ForeignKey('{}.id'.format(magic_numbers.TRANSACTION_CATEGORY_TABLE)),
        primary_key=True
    )
    amount = Column(Integer)
    notes = Column(String)

    transaction = relationship('AccountTransaction', back_populates='categorizations')
    category = relationship('TransactionCategory', back_populates='categorizations')

class Receipt(BASE): # pylint: disable=too-few-public-methods
    """SQLAlchemy class for receipts"""

    __tablename__ = magic_numbers.RECEIPT_TABLE

    id = Column(Integer, primary_key=True) # pylint: disable=invalid-name
    transaction_id = Column(
        Integer,
        ForeignKey('{}.id'.format(magic_numbers.ACCOUNT_TRANSACTION_TABLE))
    )
    image_jpeg = Column(LargeBinary)
    image_pdf = Column(LargeBinary)
    notes = Column(String)

    transaction = relationship('AccountTransaction', back_populates='receipts')

class BudgetCategory(BASE): # pylint: disable=too-few-public-methods
    """SQLAlchemy class for budget categories"""

    __tablename__ = magic_numbers.BUDGET_CATEGORY_TABLE

    id = Column(Integer, primary_key=True) # pylint: disable=invalid-name
    title = Column(String(255))
    parent = Column(
        Integer,
        ForeignKey('{}.id'.format(magic_numbers.BUDGET_CATEGORY_TABLE))
    )

class Budget(BASE): # pylint: disable=too-few-public-methods
    """SQLAlchemy class for budgets"""

    __tablename__ = magic_numbers.BUDGET_TABLE

    id = Column(Integer, primary_key=True) # pylint: disable=invalid-name
    title = Column(String(255))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    currency_id = Column(
        String(3),
        ForeignKey('{}.iso4217_code'.format(magic_numbers.CURRENCY_TABLE))
    )

    currency = relationship('Currency')
    items = relationship('BudgetItem', back_populates='budget')

class BudgetItem(BASE): # pylint: disable=too-few-public-methods
    """SQLAlchemy class for budget line items"""

    __tablename__ = magic_numbers.BUDGET_ITEM_TABLE

    id = Column(Integer, primary_key=True) # pylint: disable=invalid-name
    budget_id = Column(
        Integer,
        ForeignKey('{}.id'.format(magic_numbers.BUDGET_TABLE))
    )
    category_id = Column(
        Integer,
        ForeignKey('{}.id'.format(magic_numbers.BUDGET_CATEGORY_TABLE))
    )
    title = Column(String(255))
    notes = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    amount = Column(Integer)

    budget = relationship('Budget', back_populates='items')
    category = relationship('BudgetCategory')
