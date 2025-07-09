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
                return response.text().then(text => { throw new Error(text); });
            }
            return response.text();
        })
        .then(history => {
            historyContainer.innerHTML = `
                <div style="margin-bottom: 10px;">
                    <span style="color: #888;">[HISTORY] Git log for: ${abs_path}</span>
                </div>
                <pre>${history}</pre>
            `;
            updateStatus(`[SUCCESS] History loaded for ${abs_path}`);
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