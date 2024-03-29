let nameFile = null;
let pdfTT = null;
let currentScale = 1.3;
let currentPage = 1;
let pageNumber = 0;
let price = 0;

initPdf();

function initPdf() {
    if (pdfTT === null) {
        document_name = document.getElementById("document_name").dataset.name
        pdfTT = pdfjsLib.getDocument('https://edushare-s3.s3.amazonaws.com/' + document_name);
    }

    pdfTT.promise.then((pdf) => {
        let pdf_container = document.getElementById("pdf-container");
        pdf_container.innerHTML = "";

        console.log("Hiện có " + pdf.numPages + " trang");
        pageNumber = pdf.numPages;

        for (let i = 1; i <= pdf.numPages; ++i) {
            pdf.getPage(i).then(page => {
                let divContext = document.createElement("div");
                divContext.style.position = "relative";
                divContext.setAttribute("id", "thu" + i)

                let pdfCanvas = document.createElement("canvas");
                let context = pdfCanvas.getContext("2d");
                let pageViewPort = page.getViewport({ scale: currentScale });
                pdfCanvas.style.marginBottom = "10px";
                pdfCanvas.style.marginTop = "10px";
                pdfCanvas.style.marginLeft = "auto"
                pdfCanvas.style.marginRight = "auto"
                pdfCanvas.style.display = "block"
                pdfCanvas.width = pageViewPort.width;
                pdfCanvas.height = pageViewPort.height;
                divContext.appendChild(pdfCanvas);

                page.render({
                    canvasContext: context,
                    viewport: pageViewPort
                });
                pdf_container.append(divContext);
            }).catch(pageErr => {
                console.log(pageErr);
            });
        }
    });
}