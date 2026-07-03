const API_BASE = 'http://localhost:8000';
let adminToken = localStorage.getItem('adminToken');
let currentFiles = [];

// DOM Elements
const dashboardScreen = document.getElementById('dashboard-screen');
const logoutBtn = document.getElementById('logout-btn');

// Modal Elements
const modalOverlay = document.getElementById('modal-overlay');
const modalTitle = document.getElementById('modal-title');
const modalDesc = document.getElementById('modal-desc');
const modalConfirm = document.getElementById('modal-confirm');
const modalCancel = document.getElementById('modal-cancel');

// Tabs
const navLinks = document.querySelectorAll('.nav-links li');
const tabContents = document.querySelectorAll('.tab-content');

// Check authentication
function checkAuth() {
    if (adminToken) {
        loadAnalytics();
        loadFiles();
    } else {
        window.location.href = '/';
    }
}

// Logout Handler
logoutBtn.addEventListener('click', () => {
    adminToken = null;
    localStorage.removeItem('adminToken');
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_email');
    checkAuth();
});

// Tab Navigation
navLinks.forEach(link => {
    link.addEventListener('click', () => {
        navLinks.forEach(l => l.classList.remove('active'));
        tabContents.forEach(t => t.classList.remove('active'));
        
        link.classList.add('active');
        document.getElementById(link.dataset.tab).classList.add('active');
    });
});

// --- Analytics ---
async function loadAnalytics() {
    try {
        const res = await fetch(`${API_BASE}/agent/logs`, {
            headers: { 'Authorization': `Bearer ${adminToken}` }
        });
        if (!res.ok) throw new Error('Failed to fetch logs');
        const data = await res.json();
        
        const tbody = document.getElementById('analytics-body');
        tbody.innerHTML = '';
        
        data.logs.forEach(log => {
            // Append Z to correctly parse UTC time from SQLite
            const dateStr = log.timestamp.endsWith('Z') ? log.timestamp : log.timestamp + 'Z';
            const date = new Date(dateStr).toLocaleString();
            
            let feedbackIcon = '-';
            if (log.feedback === 1) feedbackIcon = '👍';
            if (log.feedback === -1) feedbackIcon = '👎';
            
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${date}</td>
                <td>${log.user_email}</td>
                <td>${log.query}</td>
                <td>${log.intent || '-'}</td>
                <td>${log.response_time_ms ? (log.response_time_ms / 1000).toFixed(2) + ' s' : '-'}</td>
                <td>${feedbackIcon}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error(err);
    }
}

// --- Knowledge Base ---
async function loadFiles() {
    try {
        const res = await fetch(`${API_BASE}/rag/files`, {
            headers: { 'Authorization': `Bearer ${adminToken}` }
        });
        if (!res.ok) throw new Error('Failed to fetch files');
        const data = await res.json();
        currentFiles = data.files;
        
        const ul = document.getElementById('files-ul');
        ul.innerHTML = '';
        
        currentFiles.forEach(file => {
            const li = document.createElement('li');
            li.className = 'file-item';
            li.innerHTML = `
                <span class="file-name">${file}</span>
                <button class="delete-btn" onclick="promptDelete('${file}')">🗑️</button>
            `;
            ul.appendChild(li);
        });
    } catch (err) {
        console.error(err);
    }
}

// Modal helper
function showModal(title, desc, confirmCallback) {
    document.getElementById('modal-title').textContent = title;
    document.getElementById('modal-desc').innerHTML = desc;
    document.getElementById('modal-overlay').classList.remove('hidden');
    
    const confirmBtn = document.getElementById('modal-confirm');
    const cancelBtn = document.getElementById('modal-cancel');
    
    // Use onclick to cleanly override any previous callbacks without needing cloneNode
    cancelBtn.onclick = () => {
        document.getElementById('modal-overlay').classList.add('hidden');
    };
    
    confirmBtn.onclick = () => {
        confirmCallback();
        document.getElementById('modal-overlay').classList.add('hidden');
    };
}

// Delete Flow
window.promptDelete = (filename) => {
    showModal(
        'Delete Knowledge Base File', 
        `This action will delete <strong>${filename}</strong> and ALL of its file details from the database. Are you sure?`,
        () => deleteFile(filename)
    );
};

async function deleteFile(filename) {
    try {
        const res = await fetch(`${API_BASE}/rag/file/${filename}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${adminToken}` }
        });
        if (!res.ok) throw new Error('Failed to delete');
        loadFiles();
    } catch (err) {
        console.error(err);
        alert('Error deleting file');
    }
}

// Upload Flow
const fileInput = document.getElementById('file-input');
const dropZone = document.getElementById('drop-zone');

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    if (e.dataTransfer.files.length) {
        handleFileSelect(e.dataTransfer.files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length) {
        handleFileSelect(e.target.files[0]);
    }
});

function handleFileSelect(file) {
    if (currentFiles.includes(file.name)) {
        showModal(
            'File Already Exists',
            `Would you like to replace the existing file named <strong>${file.name}</strong>?`,
            () => {
                // Secondary warning as requested
                setTimeout(() => {
                    showModal(
                        'Warning: Destructive Action',
                        'This action will delete all the file details from the database and replace them. Are you sure?',
                        () => uploadFile(file)
                    );
                }, 300);
            }
        );
    } else {
        uploadFile(file);
    }
}

async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const originalText = dropZone.querySelector('h3').textContent;
    dropZone.querySelector('h3').textContent = 'Uploading & Re-indexing...';
    
    try {
        const res = await fetch(`${API_BASE}/rag/upload`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${adminToken}` },
            body: formData
        });
        if (!res.ok) throw new Error('Upload failed');
        loadFiles();
    } catch (err) {
        console.error(err);
        alert('Upload failed');
    } finally {
        dropZone.querySelector('h3').textContent = originalText;
        fileInput.value = '';
    }
}

// --- Settings ---
document.getElementById('settings-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const newEmail = document.getElementById('new-email').value;
    const newPassword = document.getElementById('new-password').value;
    const btn = e.target.querySelector('button');
    btn.disabled = true;
    btn.textContent = 'Updating...';

    try {
        // Update Password FIRST (so the token doesn't invalidate)
        const pwdRes = await fetch(`${API_BASE}/auth/admin/password`, {
            method: 'PUT',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${adminToken}` 
            },
            body: JSON.stringify({ new_password: newPassword })
        });
        if (!pwdRes.ok) throw new Error('Failed to update password');

        // Update Email SECOND
        const emailRes = await fetch(`${API_BASE}/auth/admin/email`, {
            method: 'PUT',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${adminToken}` 
            },
            body: JSON.stringify({ new_email: newEmail })
        });
        if (!emailRes.ok) throw new Error('Failed to update email');

        alert('Credentials updated successfully!');
        
        // Logout user so they can login with new credentials
        adminToken = null;
        localStorage.removeItem('adminToken');
        checkAuth();
        
    } catch (err) {
        alert(err.message);
    } finally {
        btn.disabled = false;
        btn.textContent = 'Update Credentials';
    }
});

// Initialize
checkAuth();
