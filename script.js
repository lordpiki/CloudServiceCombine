// const { load } = require("three/examples/jsm/libs/opentype.module.js");


function setupPythonBridge() {
    new QWebChannel(qt.webChannelTransport, function(channel) {
        window.python = channel.objects.bridge;
    });
    loadFiles();
}

function getServiceIcon(service_name) {
    switch (service_name) {
        case "Dropbox":
            return "images/dpx_logo.png";
        case "Google Drive":
            return "images/google_drive_logo.png";
        case "Discord":
            return "images/discord_logo.png";
        default:
            return "images/dpx_logo.png";
    }
}


function loadFiles() {
    const files_path = "./files.json";
    const services_path = "./services.json";
    services = [];
    fetch(services_path)
        .then(response => response.json())
        .then(data => {
           services = data;
        });


    fetch(files_path)
        .then(response => response.json())
        .then(data => {
            filesList = document.getElementsByClassName('file-list');
            filesList = filesList[0];
            // window.python.logMessage(filesList);

            for (const key in data) {
                const file = data[key];
                file_name = file.file_name;
                service_id = file.service_id;
                file_id = file.uuid;
                service_id = file.service_id;
                service = services[service_id];
                logo_path = getServiceIcon(service.service_name);

                const fileRow = document.createElement('div');
                fileRow.className = 'file-row';
                fileRow.id = file_id;

                const fileNameDiv = document.createElement('div');
                fileNameDiv.className = 'file-name';
                fileNameDiv.textContent = file_name;
                fileRow.appendChild(fileNameDiv);

                const actionsDiv = document.createElement('div');
                actionsDiv.className = 'actions';

                const speedIndicatorDownload = document.createElement('div');
                speedIndicatorDownload.className = 'speed-indicator';
                speedIndicatorDownload.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-arrow-down-to-line">
                        <path d="M12 17V3" />
                        <path d="m6 11 6 6 6-6" />
                        <path d="M19 21H5" />
                    </svg>
                    <div class="upload-speed">0mb/s</div>
                `;
                actionsDiv.appendChild(speedIndicatorDownload);

                const speedIndicatorUpload = document.createElement('div');
                speedIndicatorUpload.className = 'speed-indicator';
                speedIndicatorUpload.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-arrow-up-to-line">
                        <path d="M5 3h14" />
                        <path d="m18 13-6-6-6 6" />
                        <path d="M12 7v14" />
                    </svg>
                    <div class="download-speed">0mb/s</div>
                `;
                actionsDiv.appendChild(speedIndicatorUpload);

                const separator1 = document.createElement('div');
                separator1.className = 'seperator';
                separator1.textContent = '|';
                actionsDiv.appendChild(separator1);

                const deleteButton = document.createElement('button');
                deleteButton.className = 'action-button';
                deleteButton.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#D16A7B" stroke-width="1" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-x">
                        <path d="M18 6 6 18" />
                        <path d="m6 6 12 12" />
                    </svg>
                `;
                actionsDiv.appendChild(deleteButton);

                const downloadButton = document.createElement('button');
                downloadButton.className = 'action-button';
                downloadButton.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#71E052" stroke-width="1" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-download">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                        <polyline points="7 10 12 15 17 10" />
                        <line x1="12" x2="12" y1="15" y2="3" />
                    </svg>
                `;
                actionsDiv.appendChild(downloadButton);

                const separator2 = document.createElement('div');
                separator2.className = 'seperator';
                separator2.textContent = '|';
                actionsDiv.appendChild(separator2);

                const serviceImageDiv = document.createElement('div');
                serviceImageDiv.className = 'service_image';
                serviceImageDiv.innerHTML = `
                    <img src="${logo_path}" alt="Service Logo" width="40" height="40" />
                `;
                actionsDiv.appendChild(serviceImageDiv);

                const fileSizeDiv = document.createElement('div');
                fileSizeDiv.className = 'file-size';
                fileSizeDiv.textContent = '999 MB';
                actionsDiv.appendChild(fileSizeDiv);

                fileRow.appendChild(actionsDiv);
                filesList.appendChild(fileRow);
            }
        });
}

// Call Python function to upload a file
function uploadFile() {
    window.python.uploadFile();
}