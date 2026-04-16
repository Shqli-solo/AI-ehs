# apps/ehs-ai/src/adapters/secondary/minio.py
"""MinIO 适配器 - 多模态数据存储

负责：
1. 上传监控截图和告警图片
2. 下载多模态数据
3. 生成图片访问 URL
"""
import logging
from typing import Optional, BinaryIO
from io import BytesIO

logger = logging.getLogger(__name__)


class MinIOAdapter:
    """
    MinIO 存储适配器（Secondary Port）

    用于存储多模态数据（图片、视频截图等），
    供多模态 LLM 分析和前端展示使用。
    """

    def __init__(
        self,
        endpoint: str = "localhost:9000",
        access_key: str = "minioadmin",
        secret_key: str = "minioadmin",
        bucket: str = "ehs-multimedia",
        secure: bool = False,
    ):
        self._endpoint = endpoint
        self._access_key = access_key
        self._secret_key = secret_key
        self._bucket = bucket
        self._secure = secure
        self._client = None

    def _get_client(self):
        """懒加载 MinIO 客户端"""
        if self._client is None:
            try:
                from minio import Minio
                self._client = Minio(
                    self._endpoint,
                    access_key=self._access_key,
                    secret_key=self._secret_key,
                    secure=self._secure,
                )
                # 确保 bucket 存在
                if not self._client.bucket_exists(self._bucket):
                    self._client.make_bucket(self._bucket)
            except ImportError:
                logger.warning("minio 库未安装，使用 Mock 模式")
                self._client = "mock"
            except Exception as e:
                logger.error(f"MinIO 连接失败: {e}")
                self._client = "mock"
        return self._client

    def upload_image(
        self,
        object_name: str,
        data: bytes,
        content_type: str = "image/png",
    ) -> str:
        """
        上传图片到 MinIO

        Args:
            object_name: 对象名称（如 "alerts/fire_001.png"）
            data: 图片二进制数据
            content_type: 内容类型

        Returns:
            对象访问 URL
        """
        client = self._get_client()

        if client == "mock":
            logger.info(f"[Mock] 上传图片: {object_name} ({len(data)} bytes)")
            return f"http://{self._endpoint}/{self._bucket}/{object_name}"

        try:
            stream = BytesIO(data)
            client.put_object(
                self._bucket,
                object_name,
                stream,
                length=len(data),
                content_type=content_type,
            )
            return f"http://{self._endpoint}/{self._bucket}/{object_name}"
        except Exception as e:
            logger.error(f"上传图片失败: {e}")
            return ""

    def download_image(self, object_name: str) -> Optional[bytes]:
        """
        从 MinIO 下载图片

        Args:
            object_name: 对象名称

        Returns:
            图片二进制数据
        """
        client = self._get_client()

        if client == "mock":
            logger.info(f"[Mock] 下载图片: {object_name}")
            return b""

        try:
            response = client.get_object(self._bucket, object_name)
            return response.read()
        except Exception as e:
            logger.error(f"下载图片失败: {e}")
            return None

    def get_presigned_url(
        self,
        object_name: str,
        expires_seconds: int = 3600
    ) -> str:
        """
        获取预签名 URL（用于前端直接访问）

        Args:
            object_name: 对象名称
            expires_seconds: 过期时间（秒）

        Returns:
            预签名 URL
        """
        client = self._get_client()

        if client == "mock":
            return f"http://{self._endpoint}/{self._bucket}/{object_name}"

        try:
            from datetime import timedelta
            url = client.presigned_get_object(
                self._bucket,
                object_name,
                expires=timedelta(seconds=expires_seconds),
            )
            return url
        except Exception as e:
            logger.error(f"获取预签名 URL 失败: {e}")
            return ""

    def delete_object(self, object_name: str) -> bool:
        """删除对象"""
        client = self._get_client()

        if client == "mock":
            logger.info(f"[Mock] 删除对象: {object_name}")
            return True

        try:
            client.remove_object(self._bucket, object_name)
            return True
        except Exception as e:
            logger.error(f"删除对象失败: {e}")
            return False

    def list_objects(self, prefix: str = "") -> list:
        """列出对象"""
        client = self._get_client()

        if client == "mock":
            logger.info(f"[Mock] 列出对象: prefix={prefix}")
            return []

        try:
            objects = client.list_objects(self._bucket, prefix=prefix)
            return [obj.object_name for obj in objects]
        except Exception as e:
            logger.error(f"列出对象失败: {e}")
            return []
