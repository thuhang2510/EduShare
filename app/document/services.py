from datetime import datetime
from app.model.models import Documents, Categories, DocumentCategories

class DocumentsDataService():
    def create(self, account_id, data, direction_file):
        try:
            documents = Documents()
            documents.from_dict(data)
            documents.account_id = account_id
            documents.image = direction_file

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
        
    def get_all_saved(self, account_id, limit=None):
        try:
            documents = Documents.find_all_saved(account_id, limit)
            
            return Documents.list_to_dict(documents), 0, "Get document success"
        except Exception as e:
            return None, -1, "Get document fail"
        
    def get_all_view(self, limit=None):
        try:
            documents = Documents.find_all_view(limit)
            
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
            documents = Documents.find_by_id_with_account(id)

            return Documents.to_dict_tuple(documents), 0, "Get document success"
        except Exception as e:
            return None, -1, "Get document fail"
        
    def get_by_category(self, category_name, limit):
        try:
            documents = Documents.find_by_category(category_name, limit)
            
            return Documents.list_to_dict(documents), 0, "Get document success"
        except Exception as e:
            return None, -1, "Get document fail"
        
    def get_by_category_with_paginate(self, category_name, pre_page, page):
        try:
            documents = Documents.find_by_category_with_paginate(category_name, page, pre_page)
            
            return documents, 0, "Get document success"
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
            documents = Documents.find_by_id_and_status(document_id)
            documents.view_count += 1

            documents.save_to_db()
            
            return documents.to_dict(), 0, "Update document success"
        except Exception as e:
            return None, -1, "Update document fail"
        
    def update_download(self, document_id):
        try:
            documents = Documents.find_by_id_and_status(document_id)
            documents.download_count += 1

            documents.save_to_db()
            
            return documents.to_dict(), 0, "Update document success"
        except Exception as e:
            return None, -1, "Update document fail"
        
    def search_documents(self, page, query, sort, price, cat_id):
        try:
            documents = Documents.search(page, 25, query, sort, cat_id)
            
            return documents, 0, "Get document success"
        except Exception as e:
            return None, -1, "Get document fail"
        
    def get_by_account_id_with_evaluate(self, account_id):
        try:
            documents = Documents.find_by_account_id(account_id)
            
            rea = []
            results = []
            for (*item, evaluate) in documents:
                check, indx = self.check_key_tuple(item, rea)
                if check is False:
                    rea.append((item, [evaluate]))
                    results.append({"id": item[0], 
                                    "document_name": item[1].split(".")[0], 
                                    "view_count": item[2], 
                                    "download_count": item[3], 
                                    "creation_date": item[4], 
                                    "image": item[5],
                                    "evaluate": [evaluate]})
                else:
                    rea[indx][1].append(evaluate)
                    results[indx]["evaluate"] = rea[indx][1]
            
            return results, 0, "Get document success"
        except Exception as e:
            return None, -1, "Get document fail"
    
    def check_key_tuple(self, value, results):
        for indx, result in enumerate(results):
            if(value in result):
                return True, indx
            
        return False, -1
    
    def get_by_id_tuple_with_categories(self, id):
        try:
            documents = Documents.find_by_id_tuple_with_categories(id)

            results = {}
            index = 0

            for (*item, categories) in documents:
                if index == 0:
                    results = {"id": item[0], 
                                "document_name": item[1].split(".")[0], 
                                "image": item[2],
                                "description": item[3],
                                "license": item[4],
                                "categories": [categories.to_dict()]}
                else:
                    results["categories"].append(categories.to_dict())
                
                index += 1
                        
            return results, 0, "Get document success"
        except Exception as e:
            return None, -1, "Get document fail"
        
    def get_by_id_with_account(self, id):
        try:
            document = Documents.find_by_id_tuple_with_account(id)
            
            keys = ('id', 'document_name', 'description', 'view_count', 'download_count', 'type', 'account_id', 'image', 'fullname', 'email')
            
            result = dict(zip(keys, document))
            return result, 0, "Get document success"
        except Exception as e:
            return None, -1, "Get document fail"
        
    def update_info(self, document_id, data, direction_file):
        try:
            documents = Documents.find_by_id_and_status(document_id)
            documents.description = data['description']
            documents.license = data['license']
            
            if(direction_file != '/static/images/'):
                documents.image = direction_file

            documents.modified_date = datetime.utcnow

            data_old = []
            for category_old in documents.categories:
                if category_old.name not in data['categories']: 
                    document_category = DocumentCategories.find(document_id, category_old.id)
                    document_category.delete_from_db()
                else:
                    data_old.append(category_old.name)

            for category_name in data['categories']:
                if category_name not in data_old:
                    category = Categories.find_by_name(category_name)
                    documents.categories.append(category)

            documents.save_to_db()
            
            return documents.to_dict(), 0, "Update document success"
        except Exception as e:
            return None, -1, "Update document fail"
        
    def delete(self, document_id):
        try:
            documents = Documents.find_by_id_and_status(document_id)
            documents.status = False

            documents.save_to_db()
            
            return documents.to_dict(), 0, "Delete document success"
        except Exception as e:
            return None, -1, "Delete document fail"
    
    def get_by_account_id_with_paginate(self, account_id, page, per_page, type, keyword):
        try:
            documents = Documents.find_by_account_id_with_paginate(account_id, page, per_page, type, keyword)

            if (documents != None):
                return documents, 0, "Get document success"
            
            return None, -1, "Get document fail"
        except Exception as e:
            return None, -1, "Get document fail"
        
    def get_processing_with_paginate(self, account_id, page, per_page):
        try:
            documents = Documents.get_processing(account_id, page, per_page)

            if (documents != None):
                return documents, 0, "Get documents success"
            
            return None, -1, "Get documents fail"
        except Exception as e:
            return None, -1, "Get documents fail"
        
    def get_process_fail_with_paginate(self, account_id, page, per_page):
        try:
            documents = Documents.get_process_fail(account_id, page, per_page)

            if (documents != None):
                return documents, 0, "Get documents success"
            
            return None, -1, "Get documents fail"
        except Exception as e:
            return None, -1, "Get documents fail"
        
    def get_month_stats_document(self, account_id, year):
        try:
            documents = Documents.get_month_stats_document(account_id, year)

            keys = ("month", "count")
            results = []
            
            for document in documents:
                results.append(dict(zip(keys, document)))
            
            return results, 0, "Get stats success"
        except Exception as e:
            return None, -1, "Get stats fail " + str(e)
        
    def get_month_stats_view_document(self, account_id):
        try:
            documents = Documents.get_month_stats_view_document(account_id)

            keys = ("document_name", "view")
            results = []
            
            for document in documents:
                results.append(dict(zip(keys, document)))
            
            return results, 0, "Get stats success"
        except Exception as e:
            return None, -1, "Get stats fail " + str(e)
        
    def get_month_stats_download_document(self, account_id):
        try:
            documents = Documents.get_month_stats_download_document(account_id)

            keys = ("document_name", "download")
            results = []
            
            for document in documents:
                results.append(dict(zip(keys, document)))
            
            return results, 0, "Get stats success"
        except Exception as e:
            return None, -1, "Get stats fail " + str(e)
        
    def update_processing_status(self, status, document_id):
        try:
            documents = Documents.find_by_id_and_status(document_id)
            documents.processing_status = status
            
            documents.save_to_db()
            return documents, 0, "Update success"
        except Exception as e:
            return None, -1, "Update fail " + str(e)