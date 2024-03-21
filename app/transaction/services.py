from app.model.models import Transaction

class TransactionDataService():        
    def create(self, information, type, amount, wallet_balance, account_id):
        try:
            transaction = Transaction()
            transaction.information = information
            transaction.type = type
            transaction.amount = amount
            transaction.account_id = account_id
            transaction.wallet_balance = wallet_balance

            transaction.save_to_db()
            
            return transaction.to_dict(), 0, "Create transaction success"
        except Exception as e:
            return None, -1, "Create transaction fail " + str(e)
        
