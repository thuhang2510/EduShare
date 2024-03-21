import os
from app.model.models import Documents, Categories, Evaluate

class DocumentsDataService():
    def convert_data(self, file_name):
        with open(file_name, 'rb') as file:
            binary_data = file.read()
        return binary_data

    def create(self, account_id, data):
        try:
            documents = Documents()
            documents.from_dict(data)
            documents.account_id = account_id
            documents.image = self.convert_data(os.path.join("app/static/images", data["image"].filename))

            for category_name in data['categories']:
                category = Categories.find_by_name(category_name)
                documents.categories.append(category)

            documents.save_to_db()
            
            return documents, 0, "Create document success"
        except Exception as e:
            return None, -1, "Create document fail"
        
    def get_all_new(self, limit=None):
        try:
            documents = Documents.find_all_new(limit)
            
            return Documents.list_to_dict(documents), 0, "Get document success"
        except Exception as e:
            return None, -1, "Get document fail"
        
    def get_all_saved(self, account_id):
        try:
            documents = Documents.find_all_saved(account_id)
            
            return Documents.list_to_dict(documents), 0, "Get document success"
        except Exception as e:
            return None, -1, "Get document fail"
        
    def get_all_view(self):
        try:
            documents = Documents.find_all_view()
            
            return Documents.list_to_dict(documents), 0, "Get document success"
        except Exception as e:
            return None, -1, "Get document fail"
        
    def get_by_purchase(self, id, account_id):
        try:
            documents = Documents.find_by_purchase(id, account_id)
            
            return Documents.to_dict_tuple(documents), 0, "Get document success"
        except Exception as e:
            return None, -1, "Get document fail"
        
    def get_by_id(self, id):
        try:
            documents = Documents.find_by_id_tuple(id)
            documents[0].view_count += 1
            documents[0].save_to_db()
            
            return Documents.to_dict_tuple(documents), 0, "Get document success"
        except Exception as e:
            return None, -1, "Get document fail"
        
    def get_by_category(self, category_name, limit):
        try:
            documents = Documents.find_by_category(category_name, limit)
            
            return Documents.list_to_dict(documents), 0, "Get document success"
        except Exception as e:
            return None, -1, "Get document fail"
        
    def count_evaluate(self, document):
        like = 0
        dislike = 0
        save = 0

        for evaluate in document["evaluate"]:
            if evaluate["type"] == "like":
                like += 1
            elif evaluate["type"] == "dislike":
                dislike += 1
            else:
                save += 1

        return like, dislike, save
    
    def update_view(self, document_id):
        try:
            documents = Documents.find_by_id(document_id)
            documents.view_count += 1

            documents.save_to_db()
            
            return documents.to_dict(), 0, "Get document success"
        except Exception as e:
            return None, -1, "Get document fail"