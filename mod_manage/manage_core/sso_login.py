import asyncio
import uuid
import webbrowser
import json
import websockets
import os

# 配置信息
SSO_WEBSOCKET_URL = "wss://sso.nexusmods.com"
SSO_AUTH_URL = "https://www.nexusmods.com/sso"
APPLICATION_SLUG = "wait_slug"


class NexusSSOClient:
    def __init__(self):
        self.uuid = None
        self.connection_token = None
        self.api_key = None
        self.websocket = None
        self.load_persistent_data()

    def load_persistent_data(self):
        """从本地加载持久化数据"""
        if os.path.exists("sso_data.json"):
            with open("sso_data.json", "r") as f:
                data = json.load(f)
                self.uuid = data.get("uuid")
                self.connection_token = data.get("connection_token")

    def save_persistent_data(self):
        """保存数据到本地"""
        data = {
            "uuid": self.uuid,
            "connection_token": self.connection_token,
            "api_key": self.api_key,
        }
        with open("sso_data.json", "w") as f:
            json.dump(data, f)

    async def connect(self):
        """连接到SSO WebSocket服务器"""
        print("Connecting to Nexus SSO...")
        self.websocket = await websockets.connect(SSO_WEBSOCKET_URL)

        # 生成或加载UUID
        if not self.uuid:
            self.uuid = str(uuid.uuid4())

        # 构建初始数据
        init_data = {"id": self.uuid, "token": self.connection_token, "protocol": 2}
        await self.websocket.send(json.dumps(init_data))

        # 打开浏览器进行授权
        auth_url = f"{SSO_AUTH_URL}?id={self.uuid}&application={APPLICATION_SLUG}"
        webbrowser.open(auth_url)
        print(f"请打开浏览器完成授权：{auth_url}")

    async def listen(self):
        """监听WebSocket消息"""
        try:
            async for message in self.websocket:
                response = json.loads(message)
                if response.get("success"):
                    data = response.get("data", {})
                    if "connection_token" in data:
                        self.connection_token = data["connection_token"]
                        print("已更新连接令牌：", self.connection_token)
                    elif "api_key" in data:
                        self.api_key = data["api_key"]
                        print("成功获取API密钥：", self.api_key[:10] + "...")
                        self.save_persistent_data()
                        return  # 成功获取后退出
                else:
                    print("错误：", response.get("error"))
        except Exception as e:
            print("连接异常：", str(e))
        finally:
            await self.websocket.close()


async def main():
    client = NexusSSOClient()
    try:
        await client.connect()
        await client.listen()
    except websockets.ConnectionClosed:
        print("连接意外关闭，尝试重新连接...")
        await client.connect()
        await client.listen()

    if client.api_key:
        print("\n登录成功！API密钥已保存。")
        # 这里可以使用client.api_key调用Nexus API
    else:
        print("未能获取API密钥")


if __name__ == "__main__":
    asyncio.run(main())
