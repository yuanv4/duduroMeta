import pytest
import sys
import os
from loguru import logger

# 添加services目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app', 'services'))
from chatbot_service import ChatbotFactory

@pytest.fixture
def chatbot():
    """Chatbot测试夹具"""
    return ChatbotFactory.create_chatbot(
        base_url="https://api.deepseek.com",
        api_key="sk-f23f998a866a4148b8f075278b768e6e", 
        model="deepseek-chat"
    )

def test_knowledge_base_loading():
    """测试知识库加载功能"""
    from os import path, listdir, access, R_OK
    
    base_path = "data/knowledge_base"
    logger.info(f"检查知识库路径: {base_path}")
    
    # 验证路径存在
    assert path.exists(base_path), f"知识库路径不存在: {base_path}"
    # 验证路径可读
    assert access(base_path, R_OK), f"知识库路径不可读: {base_path}"
    
    # 获取知识库文件
    files = [f for f in listdir(base_path) if not f.startswith(".")]
    logger.info(f"找到知识库文件: {files}")
    # 验证文件存在
    assert len(files) > 0, f"知识库路径为空: {base_path}"

@pytest.mark.parametrize("question,expected_keywords", [
    ("大多数人写字时用哪一只手？", ["大多数", "写字", "手"]),
    ("家里的顶灯是在我们的什么位置？", ["顶灯", "位置", "上面"]),
    ("数学书放在桌上,数学书的下面是(  )", ["数学书", "桌子", "下面"]),
    ("小强住在9楼，小李住在6楼，小强在小李的什么位置？", ["小强", "小李", "上面"]),
    ("跳水运动的跳板在水面的什么位置？", ["跳板", "水面", "上面"]),
    ("玩滑板时，向后蹬地，人会向哪里运动", ["滑板", "向后", "前面"]),
    ("射击时，子弹朝枪口的哪个方向飞行？", ["子弹", "枪口", "前面"]),
    ("划船时，向后划桨，船会向哪个方向行驶？", ["划船", "划桨", "前面"]),
    ("篮球运动中的'后仰投篮'，投篮者身体向哪个方向倾斜？", ["篮球", "后仰", "后面"]),
    ("拔河运动中，运动员要把绳子向哪个方向拉？", ["拔河", "绳子", "后面"]),
    ("看书时，从哪个方向读文字？", ["看书", "文字", "从左向右"]),
    ("测右眼视力时，需要遮挡住哪只眼睛？", ["右眼", "视力", "左眼"])
])
def test_chatbot_response_contains_expected_keywords(chatbot, question, expected_keywords):
    """测试Chatbot响应是否包含预期关键词"""
    logger.info(f"测试问题: {question}")
    
    try:
        response = chatbot.chat(question)
        logger.success(f"回答: {response}")
        
        # 验证回答包含预期关键词
        for keyword in expected_keywords:
            assert keyword in response, f"回答中未找到关键词: {keyword}"
            
    except Exception as e:
        logger.error(f"测试失败: {str(e)}")
        pytest.fail(f"问答测试失败: {str(e)}")

if __name__ == "__main__":
    logger.add(
        f"{os.path.dirname(__file__)}/logs/{os.path.basename(__file__)}.log",
        rotation="100 MB",
        retention="7 days",
        level="DEBUG"
    )
    pytest.main(["-v", "--log-level=INFO"])
