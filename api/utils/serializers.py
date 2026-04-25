from api.models.report import Report
from api.models.report_setting import ReportSetting
from api.models.transaction import Transaction
from api.models.user import User


def serialize_user(user: User) -> dict:
    return {
        "id": str(user.id),
        "name": user.name,
        "email": user.email,
        "profilePicture": user.profile_picture,
        "createdAt": user.created_at,
        "updatedAt": user.updated_at,
    }


def serialize_report_setting(setting: ReportSetting | None) -> dict | None:
    if setting is None:
        return None
    return {
        "id": str(setting.id),
        "frequency": setting.frequency,
        "isEnabled": setting.is_enabled,
        "nextReportDate": setting.next_report_date,
        "lastSentDate": setting.last_sent_date,
    }


def serialize_transaction(transaction: Transaction) -> dict:
    return {
        "id": str(transaction.id),
        "userId": transaction.user_id,
        "title": transaction.title,
        "description": transaction.description,
        "type": transaction.type,
        "amount": transaction.amount,
        "category": transaction.category,
        "receiptUrl": transaction.receipt_url,
        "recurringInterval": transaction.recurring_interval,
        "nextRecurringDate": transaction.next_recurring_date,
        "lastProcessed": transaction.last_processed,
        "isRecurring": transaction.is_recurring,
        "date": transaction.date,
        "status": transaction.status,
        "paymentMethod": transaction.payment_method,
        "createdAt": transaction.created_at,
        "updatedAt": transaction.updated_at,
    }


def serialize_report(report: Report) -> dict:
    return {
        "id": str(report.id),
        "period": report.period,
        "sentDate": report.sent_date,
        "status": report.status,
        "createdAt": report.created_at,
        "updatedAt": report.updated_at,
    }
