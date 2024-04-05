from app import create_app
import os
import aspose.words as aw

lic = aw.License()

app = create_app()

if __name__ == "__main__":
    try:
        lic.set_license("Aspose.WordsforPythonvia.NET.lic")
        print("License set successfully.")
        
    except RuntimeError as err:
        print("Không thể license")
    
    app.run(debug=True)