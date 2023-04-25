async function sendMessageToAI(inputText) {
    const requestOptions = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ input_text: inputText })
    };

    try {
        const response = await fetch('/predict', requestOptions);
        const data = await response.json();
        return data.response;
    } catch (error) {
        console.error("Error:", error);
    }
}
