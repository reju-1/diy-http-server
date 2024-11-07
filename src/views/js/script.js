// import { fetchFileAndShow } from '/js/fileActions.js';

function fetchFileAndShow(file) {
    console.log(file);
}

const apiResponse = [
    {
        "file-name": "13 Hours The Secret Soldiers of Benghazi (2016).mp4",
        size: "10.6Mb",
        modified: "2023-11-15 14:59:15",
    },
    {
        "file-name": "A Silent Voice (2016)",
        size: "700.gp",
        modified: "2024-02-06 15:49:51",
    },
    {
        "file-name": "Alice Through the Looking Glass (2016).pdf",
        size: "100.0gp",
        modified: "2023-07-19 03:55:20",
    },
    // Add more files as needed
];

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
    const images = ["png", "jpg", "jpeg", "svg"];
    const videos = ["mp4", "mkv"];

    const extension = fileName.split(".").pop().toLowerCase();
    if (images.includes(extension)) {
        return "🏞️";
    } else if (videos.includes(extension)) {
        return "▶️";
    } else if (extension === "pdf") {
        return "📕";
    } else if (extension == "zip") {
        return "📦";
    }

    return "📁";
}

// Load files on page load
window.onload = () => {
    loadFiles(apiResponse);
};
