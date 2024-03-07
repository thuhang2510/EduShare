from app.model.models import Account

class UserDataService():
    def create(self, data):
        try:
            user = Account()
            user.from_dict(data, True)
            user.save_to_db()
            
            return user, 0, "Create user success"
        except Exception as e:
            return None, -1, "Create user fail"
    
    def get_by_email(self, email):
        try:
            user =  Account.find_by_email(email)
            if user is None:
                return None, -1, "Get user fail"
            
            return user, 0, "Get user success"
        except Exception as e:
            return None, -1, "Get user fail " + str(e)
    
    def update_password(self, id, pasword):
        try:
            user = Account.find_by_id(id)
            
            if user is None:
                return None, -1, "Get user fail"
            
            user.set_password(pasword)
            user.save_to_db()
            
            return user, 0, "Update password success"
        except Exception as e:
            return None, -1, "Update password fail " + str(e)
    
    def get_by_id(self, id):
        try:
            user = Account.find_by_id(id)
            if user is None:
                return None, -1, "Get user fail"
            
            return user, 0, "Get user success"
        except Exception as e:
            return None, -1, "Get user fail " + str(e) 