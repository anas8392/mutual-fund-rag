document.addEventListener("DOMContentLoaded", () => {
    const inputField = document.getElementById("chat-input");
    const sendBtn = document.getElementById("send-btn");
    const chatWindow = document.getElementById("chat-window");
    const welcomeView = document.getElementById("welcome-view");

    function appendMessage(sender, text) {
        // Hide welcome view on first message
        if (welcomeView && welcomeView.style.display !== "none") {
            welcomeView.style.display = "none";
        }

        const bubble = document.createElement("div");
        bubble.className = "message-bubble " + (sender === "user" ? "msg-user" : "msg-bot");
        
        // Basic Markdown/URL parsing for the Bot response
        if (sender === "bot") {
            // Find Source URL string and convert to styled linking button
            const sourceRegex = /Source URL:\s*(https?:\/\/[^\s]+)/gi;
            let formattedText = text.replace(sourceRegex, "<br><a href='$1' target='_blank' class='source-link'>↗ View Data Source on Indmoney</a>");
            
            // Allow basic line breaks
            formattedText = formattedText.replace(/\n/g, "<br>");
            
            // Clean up Markdown asterisks
            formattedText = formattedText.replace(/\*\*/g, "");

            bubble.innerHTML = formattedText;
        } else {
            bubble.textContent = text;
        }

        chatWindow.appendChild(bubble);
        
        // Scroll to bottom with slight delay for dynamic size
        setTimeout(() => {
            chatWindow.scrollTop = chatWindow.scrollHeight;
        }, 50);
        
        return bubble;
    }

    async function sendMessage() {
        const query = inputField.value.trim();
        if (!query) return;

        // Clear input early
        inputField.value = "";
        
        // Render User Query
        appendMessage("user", query);

        // Render Loading State
        const loadingBubble = appendMessage("bot", "Let me check the mutual fund database...");
        loadingBubble.style.opacity = "0.7";

        try {
            // Target the FastAPI endpoint running on defaults
            const response = await fetch("http://localhost:8000/api/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ query: query })
            });

            const data = await response.json();
            
            // Remove loading bubble
            chatWindow.removeChild(loadingBubble);
            
            // Render LLM Generation
            if(data.answer) {
                appendMessage("bot", data.answer);
            } else {
                appendMessage("bot", "Error: Unrecognized response from server.");
            }

        } catch (error) {
            chatWindow.removeChild(loadingBubble);
            appendMessage("bot", "Sorry, an error occurred attempting to reach the server.");
            console.error(error);
        }
    }

    // Event Listeners
    sendBtn.addEventListener("click", sendMessage);
    
    inputField.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            e.preventDefault();
            sendMessage();
        }
    });
});
