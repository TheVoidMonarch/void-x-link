// VoidLink - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize components
    initializeUploadModal();
    initializeFileActions();
    initializeQuickActions();
    initializeNotifications();
});

// Upload Modal Functionality
function initializeUploadModal() {
    const uploadCards = document.querySelectorAll('.action-card');
    const uploadModal = document.getElementById('uploadModal');
    const closeBtn = uploadModal.querySelector('.close-btn');
    const cancelBtn = uploadModal.querySelector('.cancel-btn');
    const browseBtn = uploadModal.querySelector('.browse-btn');
    const fileInput = document.getElementById('fileInput');
    const uploadBtn = uploadModal.querySelector('.upload-btn');
    const uploadList = document.getElementById('uploadList');
    const uploadArea = uploadModal.querySelector('.upload-area');

    // Open modal when upload card is clicked
    uploadCards.forEach(card => {
        if (card.querySelector('h3').textContent === 'Upload File') {
            card.addEventListener('click', () => {
                uploadModal.classList.add('show');
            });
        }
    });

    // Close modal when close button is clicked
    closeBtn.addEventListener('click', () => {
        uploadModal.classList.remove('show');
    });

    // Close modal when cancel button is clicked
    cancelBtn.addEventListener('click', () => {
        uploadModal.classList.remove('show');
    });

    // Close modal when clicking outside the modal content
    uploadModal.addEventListener('click', (e) => {
        if (e.target === uploadModal) {
            uploadModal.classList.remove('show');
        }
    });

    // Open file browser when browse button is clicked
    browseBtn.addEventListener('click', () => {
        fileInput.click();
    });

    // Handle file selection
    fileInput.addEventListener('change', () => {
        handleFiles(fileInput.files);
    });

    // Handle drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        handleFiles(e.dataTransfer.files);
    });

    // Handle upload button click
    uploadBtn.addEventListener('click', () => {
        // Simulate upload process
        const uploadItems = uploadList.querySelectorAll('.upload-item');
        
        if (uploadItems.length === 0) {
            alert('Please select files to upload');
            return;
        }

        uploadItems.forEach(item => {
            const progressBar = item.querySelector('.upload-progress-bar');
            const status = item.querySelector('.upload-status');
            
            // Simulate upload progress
            let progress = 0;
            const interval = setInterval(() => {
                progress += 10;
                progressBar.style.width = `${progress}%`;
                
                if (progress >= 100) {
                    clearInterval(interval);
                    status.textContent = 'Completed';
                    item.classList.add('completed');
                    
                    // Add to recent files (in a real app, this would be handled by the server)
                    setTimeout(() => {
                        addToRecentFiles(item.querySelector('.upload-item-name').textContent);
                    }, 1000);
                } else {
                    status.textContent = `Uploading... ${progress}%`;
                }
            }, 300);
        });

        // Close modal after all uploads complete
        setTimeout(() => {
            uploadModal.classList.remove('show');
            uploadList.innerHTML = '';
        }, 4000);
    });
}

// Handle selected files
function handleFiles(files) {
    const uploadList = document.getElementById('uploadList');
    
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        
        // Create upload item element
        const uploadItem = document.createElement('div');
        uploadItem.className = 'upload-item';
        
        // Determine file icon based on type
        let iconClass = 'fa-file';
        if (file.type.startsWith('image/')) {
            iconClass = 'fa-file-image';
        } else if (file.type.startsWith('video/')) {
            iconClass = 'fa-file-video';
        } else if (file.type.startsWith('audio/')) {
            iconClass = 'fa-file-audio';
        } else if (file.type === 'application/pdf') {
            iconClass = 'fa-file-pdf';
        } else if (file.type.includes('word')) {
            iconClass = 'fa-file-word';
        } else if (file.type.includes('excel') || file.type.includes('spreadsheet')) {
            iconClass = 'fa-file-excel';
        } else if (file.type.includes('powerpoint') || file.type.includes('presentation')) {
            iconClass = 'fa-file-powerpoint';
        } else if (file.type.includes('zip') || file.type.includes('archive')) {
            iconClass = 'fa-file-archive';
        } else if (file.type.includes('code') || file.name.endsWith('.js') || file.name.endsWith('.html') || file.name.endsWith('.css')) {
            iconClass = 'fa-file-code';
        }
        
        // Format file size
        const fileSize = formatFileSize(file.size);
        
        uploadItem.innerHTML = `
            <div class="upload-item-icon">
                <i class="fas ${iconClass}"></i>
            </div>
            <div class="upload-item-details">
                <div class="upload-item-name">${file.name}</div>
                <div class="upload-progress">
                    <div class="upload-progress-bar" style="width: 0%"></div>
                </div>
                <div class="upload-status">${fileSize} - Ready to upload</div>
            </div>
            <div class="upload-item-actions">
                <button class="remove-upload-btn">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        // Add to upload list
        uploadList.appendChild(uploadItem);
        
        // Add remove button functionality
        const removeBtn = uploadItem.querySelector('.remove-upload-btn');
        removeBtn.addEventListener('click', () => {
            uploadItem.remove();
        });
    }
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Add file to recent files list
function addToRecentFiles(fileName) {
    const fileList = document.querySelector('.recent-files-widget .file-list');
    const firstFile = fileList.querySelector('.file-item');
    
    // Create new file item
    const newFile = document.createElement('div');
    newFile.className = 'file-item';
    
    // Determine file icon based on extension
    let iconClass = 'file-icon';
    let iconType = 'fa-file';
    
    if (fileName.endsWith('.pdf')) {
        iconClass += ' pdf';
        iconType = 'fa-file-pdf';
    } else if (fileName.endsWith('.doc') || fileName.endsWith('.docx')) {
        iconClass += ' doc';
        iconType = 'fa-file-word';
    } else if (fileName.endsWith('.xls') || fileName.endsWith('.xlsx')) {
        iconClass += ' spreadsheet';
        iconType = 'fa-file-excel';
    } else if (fileName.endsWith('.ppt') || fileName.endsWith('.pptx')) {
        iconClass += ' presentation';
        iconType = 'fa-file-powerpoint';
    } else if (fileName.endsWith('.jpg') || fileName.endsWith('.jpeg') || fileName.endsWith('.png') || fileName.endsWith('.gif')) {
        iconClass += ' image';
        iconType = 'fa-file-image';
    } else if (fileName.endsWith('.mp4') || fileName.endsWith('.avi') || fileName.endsWith('.mov')) {
        iconClass += ' video';
        iconType = 'fa-file-video';
    } else if (fileName.endsWith('.mp3') || fileName.endsWith('.wav')) {
        iconClass += ' audio';
        iconType = 'fa-file-audio';
    } else if (fileName.endsWith('.zip') || fileName.endsWith('.rar')) {
        iconClass += ' zip';
        iconType = 'fa-file-archive';
    } else {
        iconClass += ' other';
    }
    
    newFile.innerHTML = `
        <div class="${iconClass}">
            <i class="fas ${iconType}"></i>
        </div>
        <div class="file-details">
            <h4>${fileName}</h4>
            <p>Just now</p>
        </div>
        <div class="file-actions">
            <button class="action-btn"><i class="fas fa-download"></i></button>
            <button class="action-btn"><i class="fas fa-share-alt"></i></button>
            <button class="action-btn"><i class="fas fa-ellipsis-v"></i></button>
        </div>
    `;
    
    // Add to file list at the top
    fileList.insertBefore(newFile, firstFile);
    
    // Add to activity list
    addToActivityList(fileName);
}

// Add activity to activity list
function addToActivityList(fileName) {
    const activityList = document.querySelector('.activity-widget .activity-list');
    const firstActivity = activityList.querySelector('.activity-item');
    
    // Create new activity item
    const newActivity = document.createElement('div');
    newActivity.className = 'activity-item';
    
    newActivity.innerHTML = `
        <div class="activity-icon upload">
            <i class="fas fa-file-upload"></i>
        </div>
        <div class="activity-details">
            <h4>You uploaded ${fileName}</h4>
            <p>Just now</p>
        </div>
    `;
    
    // Add to activity list at the top
    activityList.insertBefore(newActivity, firstActivity);
}

// File Actions Functionality
function initializeFileActions() {
    const actionBtns = document.querySelectorAll('.file-actions .action-btn');
    
    actionBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            
            const icon = btn.querySelector('i');
            const fileName = btn.closest('.file-item').querySelector('h4').textContent;
            
            if (icon.classList.contains('fa-download')) {
                // Simulate download
                simulateDownload(fileName);
            } else if (icon.classList.contains('fa-share-alt')) {
                // Simulate share
                simulateShare(fileName);
            } else if (icon.classList.contains('fa-ellipsis-v')) {
                // Show more options (not implemented)
                alert(`More options for ${fileName}`);
            }
        });
    });
}

// Simulate file download
function simulateDownload(fileName) {
    alert(`Downloading ${fileName}...`);
    
    // In a real app, this would trigger an actual download
    setTimeout(() => {
        console.log(`Download complete: ${fileName}`);
    }, 2000);
}

// Simulate file sharing
function simulateShare(fileName) {
    const shareText = prompt(`Share ${fileName} with (enter email):`, '');
    
    if (shareText) {
        alert(`Shared ${fileName} with ${shareText}`);
        
        // Add to activity list
        const activityList = document.querySelector('.activity-widget .activity-list');
        const firstActivity = activityList.querySelector('.activity-item');
        
        // Create new activity item
        const newActivity = document.createElement('div');
        newActivity.className = 'activity-item';
        
        newActivity.innerHTML = `
            <div class="activity-icon share">
                <i class="fas fa-share-alt"></i>
            </div>
            <div class="activity-details">
                <h4>You shared ${fileName} with ${shareText}</h4>
                <p>Just now</p>
            </div>
        `;
        
        // Add to activity list at the top
        activityList.insertBefore(newActivity, firstActivity);
    }
}

// Quick Actions Functionality
function initializeQuickActions() {
    const actionCards = document.querySelectorAll('.action-card');
    
    actionCards.forEach(card => {
        card.addEventListener('click', () => {
            const action = card.querySelector('h3').textContent;
            
            switch (action) {
                case 'Upload File':
                    // Handled by upload modal
                    break;
                case 'New Folder':
                    const folderName = prompt('Enter folder name:', 'New Folder');
                    if (folderName) {
                        alert(`Created folder: ${folderName}`);
                    }
                    break;
                case 'Share Link':
                    const link = 'https://voidlink.example.com/share/' + generateRandomString(10);
                    alert(`Generated sharing link: ${link}\n\nLink copied to clipboard!`);
                    break;
                case 'Security Scan':
                    alert('Starting security scan of your files...');
                    setTimeout(() => {
                        alert('Security scan complete. No issues found.');
                    }, 2000);
                    break;
            }
        });
    });
}

// Generate random string for share links
function generateRandomString(length) {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
}

// Notifications Functionality
function initializeNotifications() {
    const notificationBtn = document.querySelector('.notification-btn');
    
    notificationBtn.addEventListener('click', () => {
        alert('Notifications:\n\n1. Mike downloaded Meeting_Notes.docx\n2. Sarah shared Project_Assets.zip with you\n3. System update scheduled for tomorrow');
        
        // Clear notification badge
        const badge = notificationBtn.querySelector('.notification-badge');
        badge.style.display = 'none';
    });
}