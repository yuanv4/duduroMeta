import pytest
from loguru import logger
import os
import sys

# 添加项目根目录和services目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app', 'services'))
from tts_service import TTSService, TTSConfig

# 配置日志
logger.add("logs/test_tts.log", rotation="10 MB", level="TRACE")

@pytest.fixture
def tts_service():
    """TTS服务测试夹具"""
    tts_config = TTSConfig(
        appid="7757288662",
        access_token="Iwm8utZ5YcKIWsXWjHBXvTY-MFO8MLiU",
        cluster="volcano_tts",
        voice_type="BV700_V2_streaming",
        language="zh",
        api_url="https://openspeech.bytedance.com/api/v1/tts",
        max_text_length=30,
        audio_folder="tests/.cache"
    )
    return TTSService(tts_config)

def test_tts_service_initialization(tts_service):
    """测试TTS服务初始化"""
    assert tts_service is not None
    assert tts_service.config.appid == "7757288662"
    assert tts_service.config.access_token == "Iwm8utZ5YcKIWsXWjHBXvTY-MFO8MLiU"

@pytest.mark.parametrize("text,expected_format", [
        ("这是一个测试", "mp3"),
        ("你好，世界", "mp3"), 
        ("语音合成测试", "mp3")
])
def test_text_to_speech_conversion(tts_service, text, expected_format):
    """测试文本转语音功能"""
    try:
        audio_file = tts_service.speak(text)
        assert os.path.exists(audio_file)
        assert audio_file.endswith(f".{expected_format}")
        logger.success(f"成功生成语音文件: {audio_file}")
    except Exception as e:
        logger.error(f"语音合成失败: {str(e)}")
        pytest.fail(f"语音合成测试失败: {str(e)}")

if __name__ == "__main__":
    pytest.main(["-v", "--log-level=INFO"])
