//Guy - i have changed many things in this file
// Function to get the current chat history from the chat window
// Function to clear the chat content


function clearChat() {
    const chatContent = document.getElementById("chatContent");
    chatContent.innerHTML = ""; // Clear all messages
     // Clear chat history from sessionStorage
    sessionStorage.removeItem("chatHistory");
    // Clear the initial message flag
    sessionStorage.removeItem('initialMessageShown'); // Clear the initial message flag
    // Fetch initial message again
    fetchInitialMessage();
}

// Function to confirm clearing the chat
function confirmClearChat() {
    if (confirm("Are you sure you want to clear the chat? This action cannot be undone.")) {
        clearChat();
    } else {
        // Do nothing if user cancels
    }
}

// Function to export chat content to PDF
function exportChatToPDF() {
    const chatContent = document.getElementById("chatContent");
    const chatMessages = chatContent.childNodes;

    const { jsPDF } = window.jspdf;
    const pdf = new jsPDF();

    let y = 10; // Starting Y position
    let pageHeight = pdf.internal.pageSize.height; // Get the height of the page
    let prevClass = '';

    chatMessages.forEach((node) => {
        if (node.nodeType === Node.ELEMENT_NODE) {
            const text = node.textContent;
            const currentClass = node.className;

            // Add extra space between different types of messages
            if (currentClass !== prevClass) {
                y += 10;
            }

            // Split text to fit within the page width
            const textLines = pdf.splitTextToSize(text, 180); // Adjust width as needed

            textLines.forEach((line) => {
                if (y + 10 > pageHeight - 10) { // If the next line will be out of the page, add a new page
                    pdf.addPage();
                    y = 10; // Reset y to start from the top
                }
                pdf.text(10, y, line);
                y += 10;
            });

            prevClass = currentClass;
        }
    });

    pdf.save("chat.pdf"); // Save the PDF with filename "chat.pdf"
}


window.onload = function() {

    // Initialize chat popup display
    const chatPopup = document.getElementById("chatPopup");
    chatPopup.style.display = "block"; // Initially display the chat popup

    // Initialize minimized chat display
    const minimizedChat = document.getElementById("minimizedChat");
    minimizedChat.style.display = "none";

    // Add event listener for chat input field to handle keydown events
    const input = document.getElementById("chatInput");
    input.addEventListener("keydown", handleKeyDown);

    // Get button elements and add event listeners
    const sendButton = document.getElementById("sendChat");
    const clearChatButton = document.getElementById("clearChatButton");
    const exportButton = document.getElementById("exportChat");
    const fullscreenChatButton = document.getElementById("fullscreenChatButton");
    const minimizeButton = document.querySelector(".minimize-button");

    // Add event listener for clearing chat
    clearChatButton.addEventListener("click", function() {
        confirmClearChat();
    });

    // Add event listener for sending chat message
    sendButton.addEventListener("click", function() {
        handleSend();
    });

    // Add event listener for exporting chat to PDF
    exportButton.addEventListener("click", function() {
        exportChatToPDF();
    });

    console.log("loading this chat history");

    // Load chat history from sessionStorage
    loadChatHistory();
    
    // Fetch initial message from server
    fetchInitialMessage();

    // Add event listener for fullscreen chat button
    fullscreenChatButton.addEventListener("click", function() {
        // Get the current chat history
        const chatHistory = getCurrentChatHistory();
        // Store chat history in sessionStorage
        sessionStorage.setItem("chatHistory", JSON.stringify(chatHistory));
        // Redirect to the full screen chat page
        window.location.href = "/fullscreen_chat";
    });

    // Add event listener for minimize button click
    minimizeButton.addEventListener("click", function() {
        // Check the current display state of the chatPopup
        if (chatPopup.style.display === "block" || chatPopup.style.display === "") {
            // If it's currently displayed, hide it and show minimizedChat
            chatPopup.style.display = "none";
            minimizedChat.style.display = "flex";
            minimizedChat.textContent = "Chat With ChatGPT"; // Set text only when minimized
        }
    });

    // Add event listener for minimizedChat click
    minimizedChat.addEventListener("click", function() {
        // Show the chatPopup and hide minimizedChat
        chatPopup.style.display = "block";
        minimizedChat.style.display = "none";
        minimizedChat.textContent = ""; // Clear text when chat is open
    });
};

// Function to fetch initial message from server
function fetchInitialMessage() {
    fetch('/initial_message', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log("Initial message received:", data.reply);
        const initialMessage = data.reply;
        // Check if initial message has already been shown
        if (!sessionStorage.getItem('initialMessageShown')) {
            displayInitialMessage(initialMessage); // Display initial message in the chat window
            sessionStorage.setItem('initialMessageShown', 'true'); // Set flag in session storage
        }
    })
    .catch(error => {
        console.error('Error in fetching initial message:', error);
    });
}

// Function to display initial message
function displayInitialMessage(message) {
    const chatContent = document.getElementById("chatContent");
    const newMessage = document.createElement("div");
    newMessage.classList.add("system-message"); 
    newMessage.textContent = message;
    chatContent.appendChild(newMessage);
    chatContent.scrollTop = chatContent.scrollHeight; // Scroll to the bottom
}

// Function to handle keydown event (e.g., Enter key to send message)
function handleKeyDown(event) {
    if (event.key === "Enter") {
        handleSend(); // Send message when Enter key is pressed
    }
}

// Function to handle sending a message
function handleSend() {
    const input = document.getElementById("chatInput");
    const message = input.value;
    if (message.trim() !== "") {
        sendMessageToGPT(message); // Call sendMessageToGPT with user's input
        const chatContent = document.getElementById("chatContent");
        const newMessage = document.createElement("div");
        newMessage.classList.add("user-message"); 
        newMessage.textContent = message;
        chatContent.appendChild(newMessage);
        input.value = ""; // Clear input field
        chatContent.scrollTop = chatContent.scrollHeight; // Scroll to the bottom
    }
}

// Function to send message to server and handle response
function sendMessageToGPT(message) {
    // Make an HTTP POST request to your Flask endpoint
    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: message }) // Send message in request body
    })
    .then(response => response.json())
    .then(data => {
        // Process the response from your Flask server
        const generatedText = data.reply;
        displayMessageFromGPT(generatedText);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Function to display message received from server (e.g., ChatGPT)
function displayMessageFromGPT(message) {
    const chatContent = document.getElementById("chatContent");
    const newMessage = document.createElement("div");
    newMessage.classList.add("bot-message");
    newMessage.textContent = message;
    chatContent.appendChild(newMessage);
    chatContent.scrollTop = chatContent.scrollHeight; // Scroll to the bottom
}


// Function to get current chat history
function getCurrentChatHistory() {
    const chatContent = document.getElementById("chatContent");
    const messages = chatContent.querySelectorAll("div");
    let chatHistory = [];

    messages.forEach((message) => {
        let className = message.className;
        let text = message.textContent;
        chatHistory.push({ className, text });
    });

    return chatHistory;
}

// Function to load chat history when returning to the home page
function loadChatHistory() {
    const chatHistoryString = sessionStorage.getItem("chatHistory");
    if (chatHistoryString) {
        try {
            const chatHistory = JSON.parse(chatHistoryString);
            const chatContent = document.getElementById("chatContent");

            // Clear existing messages
            chatContent.innerHTML = "";

            // Repopulate chat window with chat history
            chatHistory.forEach((message) => {
                const newMessage = document.createElement("div");
                newMessage.classList.add(message.className); // Add the original message class
                newMessage.textContent = message.text;
                chatContent.appendChild(newMessage);
            });

            // Scroll to the bottom of chat content
            chatContent.scrollTop = chatContent.scrollHeight;
        } catch (error) {
            console.error("Error parsing chat history from sessionStorage:", error);
        }
    }
}



