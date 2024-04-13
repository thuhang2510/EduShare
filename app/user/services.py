from datetime import datetime
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
        
    def update_download(self, id, count_download, reset_week=False):
        try:
            user = Account.find_by_id(id)
            
            if user is None:
                return None, -1, "Get user fail"
            
            user.number_download = count_download

            if(reset_week):
                user.datetime_week_reset = datetime.now()

            user.save_to_db()
            
            return user.to_dict(True), 0, "Update password success"
        except Exception as e:
            return None, -1, "Update password fail " + str(e)
        
    def update_number_ask(self, id, count_ask, reset_day=False):
        try:
            user = Account.find_by_id(id)
            
            if user is None:
                return None, -1, "Get user fail"
            
            user.number_ask = count_ask

            if(reset_day):
                user.datetime_day_reset = datetime.now()

            user.save_to_db()
            
            return user.to_dict(True), 0, "Update password success"
        except Exception as e:
            return None, -1, "Update password fail " + str(e)
        
    def get_by_id_tuple(self, id):
        try:
            user = Account.find_by_id_tuple(id)
            return user, 0, "Get user success"
        except Exception as e:
            return None, -1, "Get user fail " + str(e)