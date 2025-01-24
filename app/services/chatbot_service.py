import requests
from typing import Optional, List
from loguru import logger
from pydantic import BaseModel, HttpUrl
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter

class ChatbotConfig(BaseModel):
    base_url: HttpUrl
    api_key: str
    model: str = "deepseek-chat"
    knowledge_base_path: str = "data/knowledge_base"
    local_model_path: str = "models/text2vec-base-chinese"

class ChatbotResponse(BaseModel):
    response: str
    status_code: int
    success: bool

class Chatbot:
    def __init__(self, config: ChatbotConfig):
        logger.info("Starting chatbot initialization...")
        self.config = config
        
        logger.debug("Creating HTTP session...")
        self.session = self._create_session()
        logger.debug("HTTP session created successfully")
        
        logger.debug("Initializing knowledge base...")
        self.vector_store = self._init_knowledge_base()
        logger.debug("Knowledge base initialized successfully")
        
        logger.debug("Starting knowledge base watcher...")
        self._start_knowledge_base_watcher()
        logger.info("Chatbot initialized successfully")
        
    def _start_knowledge_base_watcher(self):
        logger.trace("Setting up knowledge base watcher thread")
        import threading
        import time
        import os
        
        def watcher():
            last_modified = self._get_knowledge_base_last_modified()
            while True:
                time.sleep(60)  # 每分钟检查一次
                current_modified = self._get_knowledge_base_last_modified()
                if current_modified > last_modified:
                    logger.info("Knowledge base files changed, reloading...")
                    self.vector_store = self._init_knowledge_base()
                    last_modified = current_modified
                    
        thread = threading.Thread(target=watcher, daemon=True)
        thread.start()
        logger.trace("Knowledge base watcher started successfully")
        
    def _get_knowledge_base_last_modified(self):
        import os
        from datetime import datetime
        
        max_mtime = 0
        for root, _, files in os.walk(self.config.knowledge_base_path):
            for f in files:
                if f.startswith("."):  # 忽略隐藏文件
                    continue
                mtime = os.path.getmtime(os.path.join(root, f))
                if mtime > max_mtime:
                    max_mtime = mtime
        return datetime.fromtimestamp(max_mtime)
        
    def _init_knowledge_base(self):
        logger.trace("Starting knowledge base initialization")
        logger.debug(f"Knowledge base path: {self.config.knowledge_base_path}")
        logger.debug(f"Local model path: {self.config.local_model_path}")
        import os
        import pickle
        from datetime import datetime, timedelta
        
        cache_dir = os.path.join(self.config.knowledge_base_path, ".cache")
        cache_file = os.path.join(cache_dir, "vector_store.pkl")
        metadata_file = os.path.join(cache_dir, "metadata.json")
        
        # 创建缓存目录
        os.makedirs(cache_dir, exist_ok=True)
        logger.trace(f"Cache directory: {cache_dir}")
        
        # 检查缓存是否有效
        if os.path.exists(cache_file) and os.path.exists(metadata_file):
            with open(metadata_file, "r") as f:
                import json
                metadata = json.load(f)
                last_modified = datetime.fromisoformat(metadata["last_modified"])
                
                # 如果知识库文件未修改且缓存未过期（7天）
                if (datetime.now() - last_modified) < timedelta(days=7):
                    # 检查缓存版本是否匹配当前文件格式
                    if metadata.get("file_format", "txt") == "md":
                        with open(cache_file, "rb") as f:
                            logger.info("Loading vector store from cache")
                            return pickle.load(f)
                    
            # 如果文件格式不匹配，清除缓存
            logger.info("Clearing outdated cache due to file format change")
            os.remove(cache_file)
            os.remove(metadata_file)
        
        # 加载知识库文档
        logger.debug("Loading knowledge base documents...")
        try:
            from langchain_community.document_loaders import TextLoader
            loader = DirectoryLoader(
                self.config.knowledge_base_path,
                glob="**/*.md",
                loader_cls=TextLoader,
                show_progress=True
            )
            logger.debug(f"Loading documents from: {self.config.knowledge_base_path}")
            documents = loader.load()
            logger.debug(f"Loaded {len(documents)} documents")
            for doc in documents:
                logger.trace(f"Document metadata: {doc.metadata}")
        except Exception as e:
            logger.error(f"Failed to load documents: {str(e)}")
            raise
        
        # 分割文档
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        texts = text_splitter.split_documents(documents)
        logger.debug(f"Split documents into {len(texts)} chunks")
        
        # 创建向量存储
        logger.debug("Creating vector store...")
        import requests
        
        # 创建带有重试机制的session
        session = requests.Session()
        retry_strategy = requests.adapters.HTTPAdapter(
            max_retries=5,
            pool_connections=10,
            pool_maxsize=10,
            pool_block=True
        )
        session.mount("https://", retry_strategy)
        
        # 初始化HuggingFaceEmbeddings，使用本地模型
        embeddings = HuggingFaceEmbeddings(
            model_name=self.config.local_model_path,
            cache_folder="models"
        )
        vector_store = FAISS.from_documents(texts, embeddings)
        logger.debug("Vector store created successfully")
        
        # 保存缓存
        with open(cache_file, "wb") as f:
            pickle.dump(vector_store, f)
            
        # 保存元数据
        with open(metadata_file, "w") as f:
            import json
            json.dump({
                "last_modified": datetime.now().isoformat(),
                "version": "1.0",
                "file_format": "md"
            }, f)
        
        logger.info("Knowledge base initialized and cached successfully")
        return vector_store
 
    def _create_session(self):
        logger.trace("Creating HTTP session with retry strategy")
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        logger.trace("HTTP session configured successfully")
        return session
        
    def chat(self, message: str) -> str:
        try:
            logger.debug(f"Received chat message: {message}")
            # 先进行知识检索
            logger.trace("Performing similarity search on vector store")
            docs_and_scores = self.vector_store.similarity_search_with_score(message, k=3)
            logger.debug(f"Found {len(docs_and_scores)} relevant documents")
            
            # 构建上下文
            context_parts = []
            for i, (doc, score) in enumerate(docs_and_scores):
                context_parts.append(
                    f"【知识片段 {i+1}】\n"
                    f"相关性评分：{score:.2f}\n"
                    f"内容：{doc.page_content}\n"
                    f"来源：{doc.metadata.get('source', '未知')}\n"
                )
            context = "\n".join(context_parts)
            
            # 构建prompt
            system_prompt = (
                "【Context】你叫兜兜龙，是一个AI学习伙伴，专门为6-12岁儿童提供学习辅导和陪伴。\n"
                "【Objective】帮助小朋友理解知识、培养学习兴趣，并提供安全友好的互动体验。\n"
                "【Situation】小朋友提出了一个问题，你需要结合相关知识给出准确且适合儿童理解的回答。\n"
                "【Task】分析以下知识片段，选择最相关的内容，组织成适合儿童理解的回答：\n"
                f"{context}\n"
                "【Action】1. 优先使用相关性最高的知识片段\n"
                "2. 对话使用MarkDown格式\n"
                "3. 用简单易懂的语言解释概念\n"
                "4. 保持友好和鼓励的语气\n"
                "5. 注明知识来源\n"
                "【Result】引导小朋友理解并记住所学内容，对学习产生更大兴趣。"
            )
            
            url = f"{self.config.base_url}/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.config.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ]
            }
            
            logger.debug(f"Sending chat request to {url}")
            response = self.session.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            return data["choices"][0]["message"]["content"]
            
        except Exception as e:
            logger.error(f"Chatbot request failed: {str(e)}")
            raise

class ChatbotFactory:
    @staticmethod
    def create_chatbot(base_url: str, api_key: str, model: str) -> Chatbot:
        config = ChatbotConfig(
            base_url=base_url,
            api_key=api_key,
            model=model
        )
        return Chatbot(config)
