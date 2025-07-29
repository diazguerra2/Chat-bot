const readline = require('readline');

// Create interface for reading user input
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

// Simple chat bot responses
const responses = {
    'hello': 'Hello! How can I help you today?',
    'hi': 'Hi there! What can I do for you?',
    'how are you': 'I\'m doing great, thank you for asking!',
    'what is your name': 'I\'m a simple chat bot created in JavaScript!',
    'help': 'You can ask me simple questions like: hello, how are you, what is your name, or type "quit" to exit.',
    'bye': 'Goodbye! Have a great day!',
    'quit': 'Goodbye! Have a great day!'
};

// Function to get bot response
function getBotResponse(userInput) {
    const input = userInput.toLowerCase().trim();
    
    // Check for exact matches first
    if (responses[input]) {
        return responses[input];
    }
    
    // Check for partial matches
    for (const key in responses) {
        if (input.includes(key)) {
            return responses[key];
        }
    }
    
    // Default response
    return "I'm not sure how to respond to that. Type 'help' for available commands.";
}

// Main chat loop
function startChat() {
    console.log('🤖 Chat Bot started! Type "quit" to exit or "help" for commands.\n');
    
    const askQuestion = () => {
        rl.question('You: ', (userInput) => {
            if (userInput.toLowerCase().trim() === 'quit') {
                console.log('Bot: Goodbye! Have a great day!');
                rl.close();
                return;
            }
            
            const response = getBotResponse(userInput);
            console.log(`Bot: ${response}\n`);
            
            // Continue the conversation
            askQuestion();
        });
    };
    
    askQuestion();
}

// Start the chat bot
startChat();
