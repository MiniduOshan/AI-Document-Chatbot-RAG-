const chatLog = document.getElementById("chatLog");
const questionInput = document.getElementById("question");
const quickReplyTray = document.getElementById("quickReplyTray");
const fileInput = document.getElementById("fileInput");
const fileStatus = document.getElementById("fileStatus");
const clearBtn = document.getElementById("clearBtn");

// 1. Define Quick Replies
const quickPrompts = [
    "Summarize this document",
    "What are the key points?",
    "Find important dates",
    "Analyze the data"
];

// 2. Render Quick Replies
function renderQuickReplies() {
    if (!quickReplyTray) return;
    quickReplyTray.innerHTML = "";
    quickPrompts.forEach(text => {
        const btn = document.createElement("button");
        btn.className = "quick-reply";
        btn.textContent = text;
        btn.onclick = () => {
            questionInput.value = text;
            document.getElementById("askForm").dispatchEvent(new Event('submit'));
        };
        quickReplyTray.appendChild(btn);
    });
}

function addMessage(role, text) {
    if (!chatLog) return null;
    const div = document.createElement("div");
    div.className = `message ${role}`;
    div.textContent = text;
    chatLog.appendChild(div);
    chatLog.scrollTop = chatLog.scrollHeight;
    return div;
}

// 3. Form Submission
const askForm = document.getElementById("askForm");
if (askForm && questionInput) {
    askForm.onsubmit = async (e) => {
        e.preventDefault();
        const text = questionInput.value.trim();
        if (!text) return;

        addMessage("user", text);
        questionInput.value = "";

        const loading = addMessage("bot", "Analyzing document...");

        try {
            const res = await fetch("/ask", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ question: text })
            });

            const data = await res.json();
            if (!res.ok) {
                throw new Error(data.error || "Request failed");
            }

            if (loading) {
                loading.textContent = data.answer || "No answer returned.";
            }
        } catch (err) {
            if (loading) {
                loading.textContent = `Error: ${err.message || "Could not reach the server."}`;
            }
        }
    };
}

if (fileInput && fileStatus) {
    fileInput.addEventListener("change", async () => {
        const file = fileInput.files && fileInput.files[0];
        if (!file) return;

        if (!file.name.toLowerCase().endsWith(".pdf")) {
            fileStatus.textContent = "Only PDF files are allowed";
            return;
        }

        fileStatus.textContent = "Uploading...";
        const formData = new FormData();
        formData.append("file", file);

        try {
            const res = await fetch("/upload", {
                method: "POST",
                body: formData
            });
            const data = await res.json();

            if (!res.ok) {
                throw new Error(data.error || "Upload failed");
            }

            fileStatus.textContent = data.filename || "Uploaded";
            addMessage("bot", `Indexed document: ${data.filename}`);
        } catch (err) {
            fileStatus.textContent = "Upload failed";
            addMessage("bot", `Upload error: ${err.message || "Could not upload file."}`);
        } finally {
            fileInput.value = "";
        }
    });
}

if (clearBtn && chatLog) {
    clearBtn.addEventListener("click", () => {
        chatLog.innerHTML = "";
        addMessage("bot", "Chat cleared. Upload a PDF and ask a question.");
    });
}

// Initialize
renderQuickReplies();
addMessage("bot", "Hello! I'm ready. Upload a PDF to begin.");