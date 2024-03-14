from app.model.models import Account

class UserDataService():        
    def update_account(self, id, data):
        try:
            user = Account.find_by_id(id)
            
            if user is None:
                return None, -1, "Get user fail"
            
            user.address = data["address"]
            user.fullname = data["fullname"]
            user.save_to_db()
            
            return user.to_dict(True), 0, "Update user success"
        except Exception as e:
            return None, -1, "Update user fail " + str(e)
        
    def update_password(self, id, password):
        try:
            user = Account.find_by_id(id)
            
            if user is None:
                return None, -1, "Get user fail"
            
            user.set_password(password)
            user.save_to_db()
            
            return user.to_dict(True), 0, "Update password success"
        except Exception as e:
            return None, -1, "Update password fail " + str(e)