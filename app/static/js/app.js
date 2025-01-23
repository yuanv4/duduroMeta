document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded and parsed');
    const chatHistory = document.getElementById('chat-history');
    const inputText = document.getElementById('input-text');
    const audioPlayer = document.getElementById('audio-player');
    
    console.log('Elements:', {
        chatHistory,
        inputText,
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
        
        // Add play button for bot messages
        if (sender === 'bot') {
            const playBtn = document.createElement('button');
            playBtn.className = 'play-audio-btn';
            playBtn.innerHTML = ''; // Play symbol
            playBtn.title = '';
            refreshPlayBtn(playBtn, true);

            timeDiv.appendChild(playBtn);
        }
        
        bubbleDiv.appendChild(textDiv);
        bubbleDiv.appendChild(timeDiv);
        messageDiv.appendChild(bubbleDiv);
        chatHistory.appendChild(messageDiv);
        // Smooth scroll to bottom with behavior: 'smooth'
        chatHistory.scrollTo({
            top: chatHistory.scrollHeight,
            behavior: 'smooth'
        });
    }

    // 播放音频
    function playAudio(url) {
        audioPlayer.src = url;
        audioPlayer.style.display = 'block';
        audioPlayer.play();
    }

    // 刷新 playBtn 按钮样式
    function refreshPlayBtn(currentBtn, isPlaying){
        if (isPlaying) {
            currentBtn.innerHTML = '&#10074;'; // Pause symbol
            currentBtn.title = '暂停播放';
            currentBtn.addEventListener('click', function() {
                audioPlayer.pause();
                refreshPlayBtn(currentBtn, false)
            });
        } else {
            currentBtn.innerHTML = '&#9658;'; // Play symbol
            currentBtn.title = '播放语音';
            currentBtn.addEventListener('click', function() {
                audioPlayer.play();
                refreshPlayBtn(currentBtn, true)
            });
        }
    }
});
