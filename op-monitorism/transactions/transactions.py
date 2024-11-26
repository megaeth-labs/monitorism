from web3 import Web3
import time
import schedule
import subprocess
import os

# 配置以太坊节点连接
rpc_url = "http://localhost:9545"  # 替换为你的本地以太坊节点地址
web3 = Web3(Web3.HTTPProvider(rpc_url))

# 检查连接状态
if not web3.is_connected():
    raise Exception("无法连接到以太坊节点")

# 目标地址
target_address = web3.to_checksum_address("0x2816Cf9c0c610810983D84475e2F44948732061f")  # 替换为目标地址

# 输出文件路径
output_file = "transactions_with_balance.txt"

# 记录已处理的最新区块高度
latest_processed_block = 0
target_value_wei = 1 * 10 ** 18
source_folder = "/home/ubuntu/workspace/mega-reth/bin/devnet/blockchain/devnet/op-reth"
current_time_stamp = time.strftime("%Y%m%d%H%M%S")
destination_folder = f"/home/ubuntu/workspace/clay_20241125_debug_faucet_zero_balance/opreth_{current_time_stamp}"
copy_command = f"cp -r {source_folder} {destination_folder}"


def fetch_new_transactions():
    global latest_processed_block

    # 获取最新区块高度
    latest_block = web3.eth.block_number
    print(f"最新区块号: {latest_block}")

    # 如果没有新块则跳过
    if latest_block <= latest_processed_block:
        print("没有新块，跳过")
        return

    with open(output_file, "a", encoding="utf-8") as file:  # 以追加模式打开文件
        # 处理新增的区块
        for block_num in range(latest_processed_block + 1, latest_block + 1):
            print(f"正在处理区块: {block_num}")

            # 获取区块数据
            block = web3.eth.get_block(block_num, full_transactions=True)
            for tx in block.transactions:
                # 检查交易是否相关
                if tx["from"] == target_address or tx["to"] == target_address:
                    # 获取当前交易后的余额
                    balance = web3.eth.get_balance(target_address, block_identifier=block_num)
                    if balance < target_value_wei:
                        subprocess.run(copy_command, shell=True, check=True)
                        print("success copy op-node")


                    # 格式化交易数据
                    tx_data = format_transaction(tx, balance)
                    print(f"发现交易: {tx['hash'].hex()}")

                    # 写入文件（追加）
                    file.write(tx_data + "\n")

    # 更新已处理的最新区块号
    latest_processed_block = latest_block
    print(f"处理完成，已更新最新区块号为: {latest_processed_block}")


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


if __name__ == "__main__":
    # 初始化已处理区块号为当前最高区块号
    latest_processed_block = web3.eth.block_number
    print(f"初始化最新处理区块号为: {latest_processed_block}")

    # 定时任务，每 10 秒检查新块
    schedule.every(10).seconds.do(fetch_new_transactions)

    print("开始定时检查新块...")
    while True:
        schedule.run_pending()
        time.sleep(1)
