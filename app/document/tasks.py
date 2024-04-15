import os
from celery import shared_task

@shared_task()
def delete_wait_file(fileName):
    file_path = f"upload_files/{fileName}"
    if os.path.exists(file_path):
        os.remove(file_path)
