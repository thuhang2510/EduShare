from app.model.models import Categories

class CategoriesDataService():    
    def get_not_parent_id(self):
        try:
            categories =  Categories.find_all_not_parent()
            if categories is None:
                return None, -1, "Get categories fail"
            
            return Categories.list_to_dict(categories), 0, "Get categories success"
        except Exception as e:
            return None, -1, "Get categories fail " + str(e)
        
    def get_by_parent_id(self, parent_id):
        try:
            categories =  Categories.find_by_parent_id(parent_id)
            if categories is None:
                return None, -1, "Get categories fail"
            
            return Categories.list_to_dict(categories), 0, "Get categories success"
        except Exception as e:
            return None, -1, "Get categories fail " + str(e)
        
    def get_all(self):
        try:
            categories =  Categories.find_all()
            if categories is None:
                return None, -1, "Get categories fail"
            
            return categories, 0, "Get categories success"
        except Exception as e:
            return None, -1, "Get categories fail " + str(e)
        
    def get_by_document_id(self, documet_id):
        try:
            categories =  Categories.find_by_document_id(documet_id)
            if categories is None:
                return None, -1, "Get categories fail"
            
            return categories, 0, "Get categories success"
        except Exception as e:
            return None, -1, "Get categories fail " + str(e)