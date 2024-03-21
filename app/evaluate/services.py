from app.model.models import Evaluate

class EvaluateDataService():        
    def create_or_delete(self, document_id, account_id, type):
        try:
            evaluate = Evaluate.find_by_type(document_id, account_id, type)
            
            if evaluate is not None:
                return self.delete(evaluate)
            
            evaluate = self.checkTypeOpposition(document_id, account_id, type)
            if evaluate is not None:
                self.delete(evaluate)
            
            evaluate = Evaluate()
            evaluate.account_id = account_id
            evaluate.document_id = document_id
            evaluate.type = type

            evaluate.save_to_db()
            
            return evaluate.to_dict(), 0, "Create evaluate success"
        except Exception as e:
            return None, -1, "Create evaluate fail " + str(e)
        
    def delete(self, evaluate):
        try:
            evaluate.delete_from_db()
            return None, 0, "Delete evaluate success"
        except Exception as e:
            return None, -1, "Delete evaluate fail " + str(e)
        
    def get(self, document_id, account_id):
        try:
            evaluate = Evaluate.find(document_id, account_id)
            return Evaluate.list_to_dict(evaluate), 0, "Get evaluate success"
        except Exception as e:
            return None, -1, "Get evaluate fail " + str(e)

    def checkTypeOpposition(self, document_id, account_id, type):
        try:
            if type == "like":
                type = "dislike"
            elif type == "dislike":
                type = "like"

            evaluate = Evaluate.find_by_type(document_id, account_id, type)
            return evaluate
        except Exception as e:
            return None