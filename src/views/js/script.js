import { loadMedia } from "./modal-script.js";

function fetchFileAndShow(file) {
    console.log(file);

    //Todo: handle pdf to open new tab
    loadMedia(file["file-name"]);
}

async function getApiResponse() {
    try {
        const response = await fetch("/api", {
            method: "GET",
            headers: {
                "Accept": "application/json",
            },
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        console.log(data);
        return data;
    } catch (error) {
        console.error("Error fetching the API response:", error);
    }
}

// Function to load files into the HTML
function loadFiles(files) {
    const fileContainer = document.getElementById("file-container");
    fileContainer.innerHTML = ""; // Clear existing content

    files.forEach((file) => {
        const fileItem = document.createElement("div");
        fileItem.classList.add("file-item");

        fileItem.innerHTML = `
            <span class="name">${getFileIcon(file["file-name"])} ${
            file["file-name"]
        }</span>
            <span class="size">${file.size}</span>
            <span class="modified">${file.modified}</span>
        `;

        fileItem.onclick = () => fetchFileAndShow(file);

        fileContainer.appendChild(fileItem);
    });
}

function getFileIcon(fileName) {
    const images = ["png", "jpg", "jpeg", "svg", "ico"];
    const videos = ["mp4", "mkv"];
    const extension = fileName.split(".").pop().toLowerCase();

    if (images.includes(extension)) {
        return "🏞️";
    } else if (videos.includes(extension)) {
        return "▶️";
    } else if (extension === "pdf") {
        return "📕";
    } else if (extension === "zip") {
        return "📦";
    }

    return "📁";
}

// Load files on page load
window.onload = async () => {
    const apiResponse = await getApiResponse();
    loadFiles(apiResponse);
};
