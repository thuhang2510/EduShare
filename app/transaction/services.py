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
        
    def get_by_account_id_with_paginate(self, account_id, page, per_page, from_date, to_date, type, result):
        try:
            transactions = Transaction.get_by_account_id_with_paginate(account_id, page, per_page, from_date, to_date, type, result)

            if(transactions is not None):
                results = {
                    "first": transactions.first,
                    "has_next": transactions.has_next,
                    "has_prev": transactions.has_prev,
                    "last": transactions.last,
                    "next_num": transactions.next_num,
                    "page": transactions.page,
                    "pages": transactions.pages,
                    "prev_num": transactions.prev_num,
                    "total": transactions.total
                }

                results["items"] = []

                for item in transactions.items:
                    results["items"].append(item.to_dict())
                    
                return results, 0, "Get transactions success"
            
            return None, -1, "Get transaction fail"
        except Exception as e:
            return None, -1, "Get transactions fail " + str(e)
        
    def get_month_stats(self, account_id, year):
        try:
            transactions = Transaction.get_month_stats_with_account_id(account_id, year)

            keys = ("month", "sum")
            results = []
            
            for transaction in transactions:
                results.append(dict(zip(keys, transaction)))
            
            return results, 0, "Get stats success"
        except Exception as e:
            return None, -1, "Get stats fail " + str(e)
        
    def get_total(self, account_id, type):
        try:
            sum = Transaction.get_total(account_id, type)

            if(sum is None):
                 return None, 0, "Get sum success"

            return sum, 0, "Get sum success"
        except Exception as e:
            return None, -1, "Get sum fail " + str(e)