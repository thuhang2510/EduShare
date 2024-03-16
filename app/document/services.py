from app.model.models import Documents, Categories, Evaluate

class DocumentsDataService():
    def create(self, account_id, data):
        try:
            documents = Documents()
            documents.from_dict(data)
            documents.account_id = account_id

            for category_name in data['categories']:
                category = Categories.find_by_name(category_name)
                documents.categories.append(category)

            documents.save_to_db()
            
            return documents, 0, "Create document success"
        except Exception as e:
            return None, -1, "Create document fail"
        
    def get_all_new(self):
        try:
            documents = Documents.find_all_new()
            
            return Documents.list_to_dict(documents), 0, "Create document success"
        except Exception as e:
            return None, -1, "Create document fail"
        
    def get_all_saved(self, account_id):
        try:
            documents = Documents.find_all_saved(account_id)
            
            return Documents.list_to_dict(documents), 0, "Create document success"
        except Exception as e:
            return None, -1, "Create document fail"
        
    def get_all_view(self):
        try:
            documents = Documents.find_all_view()
            
            return Documents.list_to_dict(documents), 0, "Create document success"
        except Exception as e:
            return None, -1, "Create document fail"