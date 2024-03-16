var scrollPositionSaved = 0;
function clickNextSavedDoc() {
    var carouselWidthSaved = document.querySelector("#carouselSavedControls .carousel-inner").scrollWidth;
    var cardWidthSaved = document.querySelector("#carouselSavedControls .carousel-item").clientWidth;

    if (scrollPositionSaved < carouselWidthSaved - cardWidthSaved * 4) {
        scrollPositionSaved += cardWidthSaved;
        document.querySelector("#carouselSavedControls .carousel-inner").scrollTo({
                left: scrollPositionSaved,
                behavior: "smooth",
            });
    }
}

function clickPrevSavedDoc() {
    var cardWidthSaved = document.querySelector("#carouselSavedControls .carousel-item").clientWidth;

    if (scrollPositionSaved > 0) {
        scrollPositionSaved -= cardWidthSaved;
        document.querySelector("#carouselSavedControls .carousel-inner").scrollTo({
                left: scrollPositionSaved,
                behavior: "smooth",
            });
    }
}

var scrollPosition = 0;

function clickPrevNewDoc(){
    var cardWidth = document.querySelector("#carouselNewControls .carousel-item").clientWidth;

    if (scrollPosition > 0) {
        scrollPosition -= cardWidth;
        document.querySelector("#carouselNewControls .carousel-inner").scrollTo({
                left: scrollPosition,
                behavior: "smooth",
            });
    }
}

function clickNextNewDoc(){
    var carouselWidth = document.querySelector("#carouselNewControls .carousel-inner").scrollWidth;
    var cardWidth = document.querySelector("#carouselNewControls .carousel-item").clientWidth;

    if (scrollPosition < carouselWidth - cardWidth * 4) {
        scrollPosition += cardWidth;
        document.querySelector("#carouselNewControls .carousel-inner").scrollTo({
                left: scrollPosition,
                behavior: "smooth",
            });
    }
}

var scrollPositionView = 0;

function clickPrevViewDoc(){
    var cardWidth = document.querySelector("#carouselViewControls .carousel-item").clientWidth;

    if (scrollPositionView > 0) {
        scrollPositionView -= cardWidth;
        document.querySelector("#carouselViewControls .carousel-inner").scrollTo({
                left: scrollPositionView,
                behavior: "smooth",
            });
    }
}

function clickNextViewDoc(){
    var carouselWidth = document.querySelector("#carouselViewControls .carousel-inner").scrollWidth;
    var cardWidth = document.querySelector("#carouselViewControls .carousel-item").clientWidth;

    if (scrollPositionView < carouselWidth - cardWidth * 4) {
        scrollPositionView += cardWidth;
        document.querySelector("#carouselViewControls .carousel-inner").scrollTo({
                left: scrollPositionView,
                behavior: "smooth",
            });
    }
}