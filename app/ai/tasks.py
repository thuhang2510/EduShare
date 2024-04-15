from celery import shared_task
from app.ai.services import AIDataService
from app.document.services import DocumentsDataService

@shared_task(ignore_result=False)
def page_pdf_and_build_vector_db(url, document_edu_name, document_id, user_id, api_key=None):
    print("vo")
    _, code, _ = AIDataService().page_pdf_and_build_vector_db(url, document_edu_name, document_id, user_id, api_key)

    print(code)
    
    status = 0
    if code == 0:
        status = 1
    else:
        status = -1

    print("update status")
        
    DocumentsDataService().update_processing_status(status, document_id)
