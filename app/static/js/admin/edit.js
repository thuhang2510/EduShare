function checkStatus(reason_content) {
    const checkbox = document.getElementById("status");
    const deletionReason = document.getElementById("deletion_reason");
    const deletionReasonContent = document.getElementById("deletion_reason_content");

    if (checkbox.checked) {
        deletionReason.style.display = "none";
        deletionReasonContent.innerHTML = `<textarea name="deletion_reason" class="form-control" rows="3"></textarea>`
    } else {
        deletionReason.style.display = "block";

        if(reason_content == "None")
            reason_content = "";
        
        deletionReasonContent.innerHTML = `<textarea name="deletion_reason" class="form-control" rows="3" required>${reason_content}</textarea>`
    }
}