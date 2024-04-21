from weasyprint import HTML

def create_pdf(content):
    try:
        HTML(string=content).write_pdf("commitment.pdf")
    except Exception as err:
        print("\nThere was an error setting the license:", err)