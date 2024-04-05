import os
import aspose.words as aw

lic = aw.License()

def convert_doc_to_pdf(file_path_old, file_path_new):
    try:
        lic.set_license("Aspose.WordsforPythonvia.NET.lic")
        print("License set successfully.")
        
        doc = aw.Document(file_path_old)
        doc.save(file_path_new)
        os.remove(file_path_old)
        return "", 0, None
    except RuntimeError as err:
        return "Không thể license", -1, None