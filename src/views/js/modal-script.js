export function loadMedia(file_url) {
    ClearAndCloseModal();

    const modal = document.querySelector(".modal-media-container");

    modal.style.display = "block"; // Showing the modal

    const fileType = file_url.split(".").pop().toLowerCase();

    let mediaElement;

    if (["jpg", "jpeg", "png", "svg", "ico"].includes(fileType)) {
        mediaElement = document.createElement("img");
        mediaElement.src = file_url;
        mediaElement.alt = file_url;
    } else if (["mp4", "mkv"].includes(fileType)) {
        mediaElement = document.createElement("video");
        mediaElement.controls = true;
        mediaElement.src = file_url;
    } else {
        modal.innerHTML = `<p>Unsupported file type: ${fileType}</p>`;
        return;
    }

    mediaElement.style.width = "100%";
    mediaElement.style.border = "2px solid #000";

    modal.appendChild(mediaElement);
}

//  Clear previous content and close the Modal
function ClearAndCloseModal() {
    const modal = document.querySelector(".modal-media-container");
    const mediaContent = modal.querySelector("img, video");

    if (mediaContent) {
        mediaContent.remove(); // Removing the current media content
    }

    if (modal) {
        modal.style.display = "none";
    }
}

// Binding globally
window.ClearAndCloseModal = ClearAndCloseModal;
