from app.model.models import Transaction, db, Purchase, Account, Documents

class PurchaseDataService():        
    def create(self, document_id, account_id, current_user_id, amount):
        try:
            document = Documents.find_by_id_and_status(document_id)
            admin = Account.find_by_permission("admin")
            current_user = Account.find_by_id(current_user_id)
            seller = Account.find_by_id(account_id)

            purchase = Purchase()
            purchase.document_id = document_id
            purchase.account_id = current_user_id
            purchase.amount = amount

            buyer_transaction = Transaction(
                information = 'Mua tài liệu: ' + document.document_name ,
                type = 'Mua tài liệu',
                amount = amount,
                result = 'Thành công',
                account_id = current_user_id
            )
            buyer_transaction.wallet_balance = current_user.coin - int(amount)
            current_user.coin -= int(amount)
            
            db.session.add(current_user)
            db.session.add(purchase)
            db.session.add(buyer_transaction)

            seller_amount = (70 / 100 * int(amount))
            seller_transaction = Transaction(
                information = 'Bán tài liệu: ' + document.document_name ,
                type = 'Bán tài liệu',
                amount = seller_amount,
                result = 'Thành công',
                account_id = account_id
            )
            seller_transaction.wallet_balance = seller.coin + seller_amount
            seller.coin += seller_amount

            db.session.add(seller)
            db.session.add(seller_transaction)

            admin_amount = (30 / 100 * int(amount))
            admin_transaction = Transaction(
                information = 'Nhận hoa hồng: ' + document.document_name,
                type = 'Nhận hoa hồng',
                amount = admin_amount,
                result = 'Thành công',
                account_id = admin.id
            )
            admin_transaction.wallet_balance = admin.coin + admin_amount
            admin.coin += admin_amount

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
