import asyncio
import websockets
import json
from web3 import Web3

# WebSocket 地址，替换为你的节点地址
ws_url = "ws://127.0.0.1:19546"

# 输出文件路径
output_file = "eth_subscribe.txt"

# 创建 Web3 实例
w3 = Web3(Web3.LegacyWebSocketProvider(ws_url))

async def subscribe_new_pending_transactions():
    async with websockets.connect(ws_url) as ws:
        # 发送订阅请求
        subscribe_request = {
            "jsonrpc": "2.0",
            "method": "eth_subscribe",
            "params": ["logs"],
            "id": 1
        }
        await ws.send(json.dumps(subscribe_request))

        prev_block_number = 0

        prev_transaction_indexes = []
        prev_log_indexes = []
        with open(output_file, "a", encoding="utf-8") as file:
            while True:
                # 接收新的消息（包含交易哈希）
                response = await ws.recv()
                data = json.loads(response)

                if 'params' in data and 'result' in data['params']:
                    tx = data['params']['result']
                    tx_hash = tx["transactionHash"]
                    tx_block_number = tx["blockNumber"]
                    tx_transaction_index = tx["transactionIndex"]
                    tx_log_index = tx["logIndex"]

                    if prev_block_number == 0:
                        prev_block_number = tx_block_number
                        continue

                    if prev_block_number == tx_block_number:
                        flag = 0
                        if tx_transaction_index in prev_transaction_indexes:
                            flag = 1
                        if tx_log_index in prev_log_indexes:
                            flag = 1
                        prev_transaction_indexes.append(tx_transaction_index)
                        prev_log_indexes.append(tx_log_index)

                        if flag == 1:
                            tx_data = (f"prev_block_number: {prev_block_number}, \n"
                            f"prev_transaction_indexes:{prev_transaction_indexes}, \n"
                            f"prev_log_indexes:{prev_log_indexes}, \n"
                            f"tx_hash:{tx_hash}, \n"
                            f"tx_block_number:{tx_block_number}, \n"
                            f"tx_transaction_index:{tx_transaction_index}, \n"
                            f"tx_log_index:{tx_log_index}, \n"
                            f"---------------------------------------------------------\n")
                            file.write(tx_data + "\n")
                    else:
                        print(f"already processed block number:{tx_block_number}")
                        prev_block_number = tx_block_number
                        prev_transaction_indexes = []
                        prev_log_indexes = []



def format_transaction(tx, balance):
    """
    格式化交易数据和余额为字符串
    """
    return (
        f"Block Number: {tx['blockNumber']}\n"
        f"Hash: {tx['hash'].hex()}\n"
        f"From: {tx['from']}\n"
        f"To: {tx['to']}\n"
        f"Value: {tx['value']} Wei\n"
        f"Gas: {tx['gas']}\n"
        f"Gas Price: {tx['gasPrice']} Wei\n"
        f"Balance After Tx: {balance} Wei\n"
        f"---------------------------------------------------------"
    )




async def main():
    await subscribe_new_pending_transactions()

# 运行主程序
if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
