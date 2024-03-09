from app.model.models import Documents, Categories

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