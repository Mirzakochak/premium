import urllib.request
import asyncio
import re

# لینک ساب اصلی که دادی
URL = "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Splitted-By-Protocol/vless.txt"

async def check_port(ip, port, timeout=3):
    """تست باز بودن پورت سرور (TCP Ping) با تایم‌اوت مشخص"""
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(ip, port), timeout=timeout
        )
        writer.close()
        await writer.wait_closed()
        return True
    except Exception:
        return False

async def process_configs():
    print("Downloading configs...")
    req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            content = response.read().decode('utf-8').splitlines()
    except Exception as e:
        print(f"Error downloading: {e}")
        return

    valid_configs = []
    configs_data = []

    # استخراج IP و پورت از فرمت vless://
    for line in content:
        if line.startswith("vless://"):
            match = re.search(r'@([^:]+):(\d+)', line)
            if match:
                host, port = match.groups()
                configs_data.append((line, host, int(port)))

    print(f"Total configs to test: {len(configs_data)}")

    async def worker(sem, config, host, port):
        async with sem:
            is_alive = await check_port(host, port)
            if is_alive:
                valid_configs.append(config)

    # تست ۱۰۰ کانفیگ به صورت همزمان برای سرعت بالا
    sem = asyncio.Semaphore(100) 
    await asyncio.gather(*(worker(sem, c, h, p) for c, h, p in configs_data))

    # ذخیره کانفیگ‌های سالم
    with open("filtered_vless.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(valid_configs))

    print(f"Valid configs saved: {len(valid_configs)}")

if __name__ == "__main__":
    asyncio.run(process_configs())
