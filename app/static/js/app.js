document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded and parsed');
    const chatHistory = document.getElementById('chat-history');
    const inputText = document.getElementById('input-text');
    const sendBtn = document.getElementById('send-btn');
    const audioPlayer = document.getElementById('audio-player');
    
    console.log('Elements:', {
        chatHistory,
        inputText,
        sendBtn,
        audioPlayer
    });

    // 发送消息
    async function sendMessage() {
        const message = inputText.value.trim();
        if (message) {
            addMessage('user', message);
            inputText.value = '';
            
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message })
                });
                
                const data = await response.json();
                addMessage('bot', data.response);
                
                if (data.audio_url) {
                    playAudio(data.audio_url);
                }
            } catch (error) {
                console.error('Error:', error);
            }
        }
    }

    // 绑定发送事件
    console.log('Binding click event to send button');
    console.log('Send button element:', sendBtn);
    sendBtn.addEventListener('click', function(e) {
        console.log('Send button clicked');
        sendMessage();
    });
    
    // 绑定回车键发送
    inputText.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // 添加消息到聊天记录
    function addMessage(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message-item ${sender}`;
        
        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'message-bubble';
        
        const textDiv = document.createElement('div');
        textDiv.className = 'message-text';
        textDiv.textContent = text;
        
        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        
        bubbleDiv.appendChild(textDiv);
        bubbleDiv.appendChild(timeDiv);
        messageDiv.appendChild(bubbleDiv);
        chatHistory.appendChild(messageDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    // 播放音频
    function playAudio(url) {
        audioPlayer.src = url;
        audioPlayer.style.display = 'block';
        audioPlayer.play();
    }
});
