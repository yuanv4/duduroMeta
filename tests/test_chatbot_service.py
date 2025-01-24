import pytest
import sys
import os
from loguru import logger

# 添加services目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app', 'services'))
from chatbot_service import ChatbotFactory

# 配置日志
logger.add("logs/test_rag.log", rotation="10 MB", level="TRACE")

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
    ("长颈鹿有多高？", ["长颈鹿", "高", "米"]),
    ("圆的周长公式是什么？", ["圆", "周长", "公式"]),
    ("蜜蜂如何传递信息？", ["蜜蜂", "跳舞", "花蜜"]),
    ("分数加减法要注意什么？", ["分数", "加减法", "通分"]),
    ("企鹅会飞吗？", ["企鹅", "飞"]),
    ("三角形内角和是多少？", ["三角形", "内角和", "180度"])
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
    pytest.main(["-v", "--log-level=INFO"])
