let openBlock = null;

// --- Terminal command animation ---
const demoCommands = [
    'confwatch web',
    'confwatch list',
    'confwatch snapshot',
    'confwatch diff ~/test-project1/.env',
    'confwatch history ~/test-project2/.env',
    'confwatch --help',
];
let cmdIndex = 0;
let charIndex = 0;
let typingTimeout = null;

function typeCommand() {
    const cmd = demoCommands[cmdIndex];
    const el = document.getElementById('animated-command');
    if (!el) return;
    el.textContent = cmd.slice(0, charIndex);
    if (charIndex < cmd.length) {
        charIndex++;
        typingTimeout = setTimeout(typeCommand, 60);
    } else {
        setTimeout(() => {
            charIndex = 0;
            cmdIndex = (cmdIndex + 1) % demoCommands.length;
            typeCommand();
        }, 1200);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    typeCommand();
});

document.addEventListener("DOMContentLoaded", function() { 
    console.log("[INFO] ConfWatch Terminal initialized");
    loadFiles(); 
});

function loadFiles() {
    // Предотвращаем стандартное поведение браузера
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    
    updateStatus("[INFO] Scanning filesystem for monitored files...");
    fetch("/api/files")
        .then(response => response.json())
        .then(data => {
            displayFiles(data.files);
            updateStatus(`[SUCCESS] Found ${data.files.length} monitored files`);
        })
        .catch(error => {
            console.error("[ERROR] Failed to load files:", error);
            document.getElementById("fileList").innerHTML = "<div class=\"error\">[ERROR] Failed to connect to ConfWatch daemon. Check if service is running.</div>";
            updateStatus("[ERROR] Connection failed");
        });
}

function updateStatus(message) {
    document.getElementById("status").textContent = message;
    console.log(message);
}

function displayFiles(files) {
    const fileList = document.getElementById("fileList");
    if (files.length === 0) {
        fileList.innerHTML = "<div class=\"loading\">[INFO] No files configured for monitoring. Edit config.yml to add files.</div>";
        return;
    }
    
    fileList.innerHTML = files.map(file => `
        <div class="file-item" id="block-${btoa(file.abs_path)}">
            <div class="file-item-main">
                <div class="file-info">
                    <div class="file-name">${file.name}</div>
                    <div class="file-status">
                        ${file.exists ? "[OK] File exists" : "[MISSING] File not found"} | 
                        ${file.history_count > 0 ? `[HISTORY] ${file.history_count} snapshots` : "[NEW] No history"}
                    </div>
                </div>
                <div class="file-actions">
                    ${file.history_count > 1 ? 
                        `<button class="btn" onclick="showDiff('${file.abs_path}')">[DIFF]</button>` :
                        `<button class="btn" disabled>[DIFF]</button>`
                    }
                    ${file.history_count > 0 ? 
                        `<button class="btn" onclick="showHistory('${file.abs_path}')">[HISTORY]</button>` :
                        `<button class="btn" disabled>[HISTORY]</button>`
                    }
                </div>
            </div>
            <div class="diff-container" id="diff-${btoa(file.abs_path)}" style="display:none;"></div>
            <div class="history-container" id="history-${btoa(file.abs_path)}" style="display:none;"></div>
        </div>
    `).join("");
}

function showDiff(abs_path) {
    closeOpenBlock();
    updateStatus(`[INFO] Loading diff for ${abs_path}...`);
    const diffId = `diff-${btoa(abs_path)}`;
    const diffContainer = document.getElementById(diffId);
    diffContainer.style.display = "block";
    diffContainer.innerHTML = "<div class=\"loading\">[LOADING] Analyzing file differences...</div>";
    openBlock = diffContainer;
    
    fetch(`/api/diff?file=${encodeURIComponent(abs_path)}`)
        .then(response => {
            if (!response.ok) {
                return response.text().then(text => { throw new Error(text); });
            }
            return response.text();
        })
        .then(diff => {
            if (diff.trim() === "") {
                diffContainer.innerHTML = "<div class=\"loading\">[INFO] No differences found - files are identical.</div>";
            } else {
                diffContainer.innerHTML = `
                    <div style="margin-bottom: 10px;">
                        <span style="color: #888;">[DIFF] Showing differences for: ${abs_path}</span>
                    </div>
                    <div id="diff2html-block"></div>
                `;
                const target = document.getElementById("diff2html-block");
                target.innerHTML = Diff2Html.html(diff, {
                    drawFileList: true,
                    matching: "lines",
                    outputFormat: "side-by-side"
                });
            }
            updateStatus(`[SUCCESS] Diff loaded for ${abs_path}`);
        })
        .catch(error => {
            console.error("[ERROR] Failed to load diff:", error);
            diffContainer.innerHTML = `<div class="error">[ERROR] Failed to load diff: ${error.message}</div>`;
            updateStatus("[ERROR] Diff loading failed");
        });
}

function showHistory(abs_path) {
    closeOpenBlock();
    updateStatus(`[INFO] Loading history for ${abs_path}...`);
    const historyId = `history-${btoa(abs_path)}`;
    const historyContainer = document.getElementById(historyId);
    historyContainer.style.display = "block";
    historyContainer.innerHTML = "<div class=\"loading\">[LOADING] Retrieving file history...</div>";
    openBlock = historyContainer;

    fetch(`/api/history?file=${encodeURIComponent(abs_path)}`)
        .then(response => {
            if (!response.ok) {
                return response.json().then(obj => { throw new Error(obj.error || 'Unknown error'); });
            }
            return response.json();
        })
        .then(data => {
            if (!data.history || data.history.length === 0) {
                historyContainer.innerHTML = '<div class="loading">[INFO] No history found for this file.</div>';
                return;
            }
            
            // Находим оригинальный путь файла из списка файлов
            const fileList = document.getElementById("fileList");
            const fileItems = fileList.querySelectorAll('.file-item');
            let originalPath = abs_path; // fallback
            
            for (let item of fileItems) {
                const fileInfo = item.querySelector('.file-name');
                if (fileInfo && item.id === `block-${btoa(abs_path)}`) {
                    originalPath = fileInfo.textContent;
                    break;
                }
            }
            
            // Render list with radio buttons
            let html = `<div style="margin-bottom: 10px;"><span style="color: #888;">[HISTORY] Git log for: ${abs_path}</span></div>`;
            html += '<form id="history-diff-form">';
            data.history.forEach((entry, idx) => {
                // Извлекаем путь и комментарий из сообщения коммита
                let lines = entry.message.split('\n');
                let firstLine = lines[0];
                let comment = lines.slice(1).join('\n').trim(); // Все строки кроме первой
                
                // Убираем "Snapshot: " и " at YYYY-MM-DD HH:MM:SS" из первой строки
                let path = firstLine.replace(/^Snapshot: /, '').replace(/ at \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/, '');
                
                // Формируем финальное сообщение
                let displayText = path;
                if (comment) {
                    displayText += ` - ${comment}`;
                }
                displayText += ` [${entry.hash.slice(0,8)}]`;
                
                html += `<div style="margin-bottom:4px;">
                    <input type="checkbox" class="terminal-checkbox" name="commit" value="${entry.hash}" id="commit_${idx}" />
                    <label for="commit_${idx}" style="color:#00ff00;cursor:pointer;">[${entry.date.slice(0,19).replace('T',' ')}] ${displayText}</label>
                    <button type="button" class="btn" style="margin-left:10px;font-size:10px;padding:2px 6px;" onclick="copyHash('${entry.hash}')" title="Copy full hash">[COPY]</button>
                    <button type="button" class="btn" style="margin-left:5px;font-size:10px;padding:2px 6px;background-color:#ff6600;" onclick="rollbackFile('${originalPath}', '${entry.hash}')" title="Rollback to this commit">[ROLLBACK]</button>
                </div>`;
            });
            html += '</form>';
            html += '<button type="button" class="btn" id="show-diff-btn" disabled>[SHOW DIFF]</button>';
            html += '<div id="custom-diff-result"></div>';
            historyContainer.innerHTML = html;

            // Logic for enabling button and showing diff
            const form = document.getElementById('history-diff-form');
            const btn = document.getElementById('show-diff-btn');
            let selected = [];
            
            // Предотвращаем отправку формы при нажатии Enter
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                e.stopPropagation();
                return false;
            });
            
            form.addEventListener('change', function() {
                selected = Array.from(form.elements['commit'])
                    .filter(el => el.checked)
                    .map(el => el.value);
                btn.disabled = selected.length !== 2;
            });
            btn.addEventListener('click', function() {
                if (selected.length !== 2) return;
                btn.disabled = true;
                updateStatus(`[INFO] Loading diff between selected snapshots...`);
                
                // Находим записи в истории для выбранных коммитов
                const selectedEntries = data.history.filter(entry => selected.includes(entry.hash));
                
                // Сортируем по дате (старый -> новый)
                selectedEntries.sort((a, b) => new Date(a.date) - new Date(b.date));
                
                // Берем хеши в правильном порядке (старый, новый)
                const from = selectedEntries[0].hash;
                const to = selectedEntries[1].hash;
                
                const diffDiv = document.getElementById('custom-diff-result');
                diffDiv.innerHTML = '<div class="loading">[LOADING] Calculating diff...</div>';
                fetch(`/api/diff_between?file=${encodeURIComponent(abs_path)}&from=${from}&to=${to}`)
                    .then(resp => resp.text())
                    .then(diff => {
                        if (!diff.trim()) {
                            diffDiv.innerHTML = '<div class="loading">[INFO] No differences found between selected snapshots.</div>';
                        } else {
                            diffDiv.innerHTML = `<div id="diff2html-custom"></div>`;
                            const target = document.getElementById('diff2html-custom');
                            target.innerHTML = Diff2Html.html(diff, {
                                drawFileList: true,
                                matching: "lines",
                                outputFormat: "side-by-side"
                            });
                        }
                        updateStatus(`[SUCCESS] Diff loaded between selected snapshots.`);
                        btn.disabled = false;
                    })
                    .catch(err => {
                        diffDiv.innerHTML = `<div class="error">[ERROR] Failed to load diff: ${err.message}</div>`;
                        updateStatus('[ERROR] Diff loading failed');
                        btn.disabled = false;
                    });
            });
        })
        .catch(error => {
            console.error("[ERROR] Failed to load history:", error);
            historyContainer.innerHTML = `<div class="error">[ERROR] Failed to load history: ${error.message}</div>`;
            updateStatus("[ERROR] History loading failed");
        });
}

function closeOpenBlock() {
    if (openBlock) {
        openBlock.style.display = "none";
        openBlock.innerHTML = "";
        openBlock = null;
    }
}

function copyHash(hash) {
    // Предотвращаем стандартное поведение браузера
    event.preventDefault();
    event.stopPropagation();
    
    navigator.clipboard.writeText(hash).then(function() {
        updateStatus(`[SUCCESS] Hash ${hash.slice(0,8)} copied to clipboard`);
    }).catch(function(err) {
        updateStatus(`[ERROR] Failed to copy hash: ${err}`);
    });
}

function showConfirmDialog(message, onConfirm) {
    const modal = document.getElementById('confirmModal');
    const confirmMessage = document.getElementById('confirmMessage');
    const confirmYes = document.getElementById('confirmYes');
    const confirmNo = document.getElementById('confirmNo');
    
    confirmMessage.innerHTML = message;
    modal.style.display = 'flex';
    
    // Обработчики событий
    const handleConfirm = (e) => {
        if (e) {
            e.preventDefault();
            e.stopPropagation();
        }
        modal.style.display = 'none';
        onConfirm();
        // Удаляем обработчики
        confirmYes.removeEventListener('click', handleConfirm);
        confirmNo.removeEventListener('click', handleCancel);
        document.removeEventListener('keydown', handleKeydown);
        modal.removeEventListener('click', handleModalClick);
    };
    
    const handleCancel = (e) => {
        if (e) {
            e.preventDefault();
            e.stopPropagation();
        }
        modal.style.display = 'none';
        // Удаляем обработчики
        confirmYes.removeEventListener('click', handleConfirm);
        confirmNo.removeEventListener('click', handleCancel);
        document.removeEventListener('keydown', handleKeydown);
        modal.removeEventListener('click', handleModalClick);
    };
    
    const handleKeydown = (e) => {
        if (e.key === 'Enter') {
            handleConfirm();
        } else if (e.key === 'Escape') {
            handleCancel();
        }
    };
    
    const handleModalClick = (e) => {
        if (e.target === modal) {
            handleCancel();
        }
    };
    
    confirmYes.addEventListener('click', handleConfirm);
    confirmNo.addEventListener('click', handleCancel);
    document.addEventListener('keydown', handleKeydown);
    modal.addEventListener('click', handleModalClick);
    
    // Фокус на кнопку подтверждения
    confirmYes.focus();
}

function rollbackFile(filePath, commitHash) {
    // Предотвращаем стандартное поведение браузера
    event.preventDefault();
    event.stopPropagation();
    
    const message = `
        <div style="margin-bottom: 15px;">
            <strong>[WARNING]</strong> You are about to rollback a file to a previous state.
        </div>
        <div style="margin-bottom: 10px;">
            <strong>File:</strong> ${filePath}<br>
            <strong>Target Commit:</strong> ${commitHash.slice(0,8)}<br>
            <strong>Action:</strong> Restore file content from commit ${commitHash.slice(0,8)}
        </div>
        <div style="color: #ff6600; font-weight: bold;">
            This action will:
            <ul style="margin: 10px 0; padding-left: 20px;">
                <li>Overwrite the current file content</li>
                <li>Create a new snapshot with rollback comment</li>
                <li>Cannot be undone automatically</li>
            </ul>
        </div>
        <div style="color: #ffff00;">
            Are you sure you want to proceed?
        </div>
    `;
    
    showConfirmDialog(message, () => {
        updateStatus(`[INFO] Rolling back ${filePath} to commit ${commitHash.slice(0,8)}...`);
        
        fetch('/api/rollback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                file: filePath,
                commit_hash: commitHash
            })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => { 
                    throw new Error(data.error || `HTTP ${response.status}`); 
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                updateStatus(`[SUCCESS] ${data.message}`);
                // Обновляем историю после rollback
                setTimeout(() => {
                    // Находим абсолютный путь для обновления истории
                    const fileList = document.getElementById("fileList");
                    const fileItems = fileList.querySelectorAll('.file-item');
                    let absPath = filePath; // fallback
                    
                    for (let item of fileItems) {
                        const fileInfo = item.querySelector('.file-name');
                        if (fileInfo && fileInfo.textContent === filePath) {
                            absPath = item.querySelector('.file-status').textContent.includes('[OK]') ? 
                                     item.querySelector('.file-name').textContent : filePath;
                            break;
                        }
                    }
                    showHistory(absPath);
                }, 1000);
            } else {
                updateStatus(`[ERROR] ${data.error}`);
            }
        })
        .catch(error => {
            console.error("[ERROR] Rollback failed:", error);
            updateStatus(`[ERROR] Failed to rollback: ${error.message}`);
        });
    });
}

function logout() {
    // Предотвращаем стандартное поведение браузера
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    
    updateStatus("[INFO] Logging out...");
    
    fetch('/api/auth/logout', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateStatus("[SUCCESS] Logged out successfully");
            // Redirect to login page
            window.location.href = '/login';
        } else {
            updateStatus("[ERROR] Logout failed");
        }
    })
    .catch(error => {
        console.error("[ERROR] Logout failed:", error);
        updateStatus("[ERROR] Logout failed");
        // Redirect to login page anyway
        window.location.href = '/login';
    });
}