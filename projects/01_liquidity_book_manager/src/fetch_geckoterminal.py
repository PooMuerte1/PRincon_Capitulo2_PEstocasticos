import requests
import json

def main():
    network = "avax"
    wavax_address = "0xb31f66aa3c1e785363f0875a1b74e27b85fd66c7"
    url = f"https://api.geckoterminal.com/api/v2/networks/{network}/tokens/{wavax_address}/pools"
    headers = {"Accept": "application/json;version=20230302"}
    
    print(f"Fetching pools for WAVAX on Avalanche from GeckoTerminal API...")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            pools = data.get("data", [])
            print(f"Found {len(pools)} pools:")
            for p in pools:
                attributes = p.get("attributes", {})
                name = attributes.get("name")
                dex = attributes.get("dex_id")
                address = attributes.get("address")
                volume = float(attributes.get("volume_usd", {}).get("h24") or 0)
                reserve = float(attributes.get("reserve_in_usd") or 0)
                print(f"- Name: {name} | DEX: {dex} | Address: {address} | 24h Vol: ${volume:,.2f} | TVL: ${reserve:,.2f}")
        else:
            print("Failed to fetch pools:", response.text)
    except Exception as e:
        print("Error occurred:", e)

if __name__ == "__main__":
    main()
