import asyncio  # 导入异步IO模块
import aiohttp  # 导入异步HTTP请求库
import random  # 导入随机数生成模块
import string  # 导入字符串处理模块
import time  # 导入时间模块

# 生成一个随机的指定长度的 ID（字母+数字组合）
def generate_random_id(length=4):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

# 异步检查 Minecraft ID 是否可用
async def check_minecraft_username(session, username):
    url = f"https://api.mojang.com/users/profiles/minecraft/{username}"  # 构建查询URL
    async with session.get(url) as response:  # 发送异步GET请求
        if response.status == 404:  # 如果状态码是404，表示ID可用
            return f"✅ {username} 可用！", username
        elif response.status == 200:  # 如果状态码是200，表示ID已被注册
            data = await response.json()  # 解析响应为JSON
            uuid = data.get("id")  # 获取UUID
            namemc_url = f"https://namemc.com/profile/{uuid}"  # 构建NameMC页面URL
            return f"❌ {username} 已被注册，UUID: {uuid}, NameMC 页面: {namemc_url}", None
        else:  # 其他状态码表示查询失败
            return f"❌ {username} 查询失败，状态码: {response.status}", None

# 任务管理：并发查询多个 ID
async def main(num_to_check=100, max_concurrent=50, id_length=4):
    checked_names = set()  # 存储已查询的 ID，防止重复
    available_ids = []  # 存储可用 ID
    semaphore = asyncio.Semaphore(max_concurrent)  # 控制并发量

    async with aiohttp.ClientSession() as session:  # 创建异步HTTP会话
        tasks = []  # 存储任务

        for _ in range(num_to_check):  # 循环生成指定数量的ID
            username = generate_random_id(id_length)  # 生成随机ID

            # 确保不会重复查询相同的 ID
            while username in checked_names:  # 如果ID已被查询过，重新生成
                username = generate_random_id(id_length)

            checked_names.add(username)  # 将ID添加到已查询集合中

            # 使用信号量控制并发量
            async def fetch(username):  # 定义异步任务
                async with semaphore:  # 使用信号量控制并发
                    result, available = await check_minecraft_username(session, username)  # 查询ID是否可用
                    print(result)  # 打印查询结果
                    with open("random_results.txt", "a", encoding="utf-8") as result_file:  # 打开结果文件
                        result_file.write(result + "\n")  # 将结果写入文件
                    if available:  # 如果ID可用
                        available_ids.append(available)  # 将ID添加到可用ID列表中

            tasks.append(fetch(username))  # 将任务添加到任务列表中

        await asyncio.gather(*tasks)  # 并发执行所有任务

    # 将所有可用 ID 一次性写入文件
    with open("available_ids.txt", "a", encoding="utf-8") as available_file:  # 打开可用ID文件
        for available in available_ids:  # 遍历可用ID列表
            available_file.write(available + "\n")  # 将可用ID写入文件

    print(f"查询完成，找到 {len(available_ids)} 个可用 ID，结果已保存至 available_ids.txt")  # 打印查询完成信息

# 运行主函数
if __name__ == "__main__":
    print("欢迎使用 Minecraft ID 批量查询工具！😁")  # 打印欢迎信息
    print()  # 添加空行

    print("本工具用于查询随机生成的 ID 是否已被注册 不要用作非法用途😤")  # 打印工具用途说明
    print()  # 添加空行

    print("因为使用的是Mojang的API所以不完全准确 3字ID结果极大可能已经全部被使用😣")  # 打印API准确性说明
    print()  # 添加空行

    print("你可以自行上https://namemc.com/minecraft-names检索🫡")  # 提供手动检索链接
    print()  # 添加空行

    print("查询结果将保存在 'random_results.txt'，可用 ID 将保存在 'available_ids.txt'😏")  # 打印结果保存位置
    print()  # 添加空行

    print("Made by B站up猪:Chifishfish 已开源到Github🤗")  # 打印作者信息
    print()  # 添加空行

    while True:
        try:
            num_to_check = int(input("\n请输入要查询的 ID 数量: "))  # 提示用户输入查询ID数量
            id_length = int(input("请输入要生成的 ID 长度 (3~16位): "))  # 提示用户输入ID长度
            if id_length < 3 or id_length > 16:  # 检查ID长度是否在有效范围内
                raise ValueError("ID 长度必须在 3 到 16 之间。")
            max_concurrent = int(input("请输入脚本同时请求查询次数的最大数量（推荐 50~100）: "))  # 提示用户输入最大并发量

            asyncio.run(main(num_to_check=num_to_check, max_concurrent=max_concurrent, id_length=id_length))  # 运行主函数
            
        except ValueError as ve:  # 捕获值错误异常
            print(f"输入不符合要求！: {ve}")  # 打印错误信息
            continue  # 重新开始循环，让用户重新输入
        except Exception as e:  # 捕获其他异常
            print(f"发生错误！：{e}")  # 打印错误信息
        
        # 询问用户是否继续
        choice = input("\n是否继续查询？(y/n): ").strip().lower()  # 提示用户是否继续查询
        if choice != 'y':  # 如果用户选择不继续
            print("程序已退出，再见!")  # 打印退出信息
            break  # 退出循环
        else:
            print("即将要开始下一轮查询...")  # 打印继续查询信息
            time.sleep(1)  # 让用户有时间阅读上一次查询的结果