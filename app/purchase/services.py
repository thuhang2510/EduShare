from app.model.models import Transaction, db, Purchase, Account, Documents

class PurchaseDataService():        
    def create(self, document_id, account_id, current_user_id, amount):
        try:
            document = Documents.find_by_id(document_id)
            admin = Account.find_by_permission("admin")
            current_user = Account.find_by_id(current_user_id)
            seller = Account.find_by_id(account_id)

            purchase = Purchase()
            purchase.document_id = document_id
            purchase.account_id = current_user_id
            purchase.amount = amount
            current_user.coin -= int(amount)
            
            db.session.add(current_user)
            db.session.add(purchase)

            seller_transaction = Transaction(
                information = 'Bán tài liệu: ' + document.document_name ,
                type = 'Bán tài liệu',
                amount = amount,
                result = 'Thành công',
                account_id = account_id
            )
            seller_transaction.wallet_balance = seller.coin + (70 / 100 * int(amount))
            seller.coin += (70 / 100 * int(amount))

            db.session.add(seller)
            db.session.add(seller_transaction)

            admin_transaction = Transaction(
                information = 'Nhận hoa hồng: ' + document.document_name,
                type = 'Nhận hoa hồng',
                amount = amount,
                result = 'Thành công',
                account_id = admin.id
            )
            admin_transaction.wallet_balance = admin.coin + (30 / 100 * int(amount))
            admin.coin += (30 / 100 * int(amount))

            db.session.add(admin)
            db.session.add(admin_transaction)

            db.session.commit()
            
            return purchase.to_dict(), 0, "Create purchase success"
        except Exception as e:
            return None, -1, "Create purchase fail " + str(e)
        
    def get(self, document_id, account_id):
        try:
            purchase = Purchase.find(document_id, account_id)
            return purchase.to_dict(), 0, "Get purchase success"
        except Exception as e:
            return None, -1, "Get purchase fail " + str(e)
