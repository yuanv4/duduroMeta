// Message queue for managing chat history
const messageQueue = [];
const MAX_MESSAGES = 3;

// Load markdown renderer
const marked = window.marked;
marked.setOptions({
  breaks: true,
  gfm: true,
  sanitize: true
});

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded and parsed');
    const chatHistory = document.getElementById('chat-history');
    const inputText = document.getElementById('input-text');
    const audioPlayer = document.getElementById('audio-player');

    // Initialize chatbot and show welcome message
    async function initializeChat() {
        try {
            // Add slight delay to ensure DOM is fully ready
            await new Promise(resolve => setTimeout(resolve, 300));
            addMessage('bot', "你好呀！我是兜兜龙，一个专门帮助小朋友学习的AI小伙伴哦！");
        } catch (error) {
            console.error('Initialization error:', error);
        }
    }

    // Ensure initialization runs after all DOM elements are ready
    setTimeout(() => {
        initializeChat();
    }, 500);
    
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
        if (sender === 'bot') {
            textDiv.innerHTML = marked.parse(text);
        } else {
            textDiv.textContent = text;
        }
        
        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        
        // Add play button for bot messages
        if (sender === 'bot') {
            const playBtn = document.createElement('button');
            playBtn.className = 'play-audio-btn';
            playBtn.innerHTML = ''; // Play symbol
            playBtn.title = '';
            bubbleDiv.appendChild(playBtn);

            refreshPlayBtn(playBtn, true);
        }
        
        bubbleDiv.appendChild(textDiv);
        bubbleDiv.appendChild(timeDiv);
        messageDiv.appendChild(bubbleDiv);
        chatHistory.appendChild(messageDiv);
        
        // 添加新消息到队列
        messageQueue.push(messageDiv);
        
        // 如果超过最大消息数量，移除最老的消息
        if (messageQueue.length > MAX_MESSAGES) {
            const oldestMessage = messageQueue.shift();
            oldestMessage.remove();
        }
    }

    // 播放音频
    function playAudio(url) {
        audioPlayer.src = url;
        audioPlayer.style.display = 'block';
        audioPlayer.play();
    }

    // 刷新 playBtn 按钮样式
    function refreshPlayBtn(currentBtn) {
        const isPlaying = !audioPlayer.paused;
        currentBtn.innerHTML = isPlaying ? '&#10074;' : '&#9658;';
        currentBtn.title = isPlaying ? '暂停播放' : '播放语音';
        currentBtn.classList.toggle('playing', isPlaying);
    }

    // 处理播放按钮点击
    function handlePlayBtnClick() {
        if (audioPlayer.paused || audioPlayer.ended) {
            audioPlayer.currentTime = 0;
            audioPlayer.play();
        } else {
            audioPlayer.pause();
        }
    }

    // 初始化音频播放器事件
    function initAudioPlayer() {
        // 为audioPlayer添加事件监听
        ['play', 'pause'].forEach(event => {
            audioPlayer.addEventListener(event, () => {
                const playBtn = document.querySelector('.play-audio-btn');
                if (playBtn) {
                    refreshPlayBtn(playBtn);
                }
            });
        });

        // 点击事件委托
        document.addEventListener('click', function(e) {
            if (e.target.classList.contains('play-audio-btn')) {
                handlePlayBtnClick();
            }
        });
    }

    // 初始化音频播放器
    initAudioPlayer();
});
