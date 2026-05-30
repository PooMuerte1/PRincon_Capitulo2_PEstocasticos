import requests
import json

def main():
    network = "avax"
    pool_address = "0xf01449c0ba930b6e2caca3def3ccbd7a3e589534"
    url = f"https://api.geckoterminal.com/api/v2/networks/{network}/pools/{pool_address}/ohlcv/minute"
    params = {
        "aggregate": 1,
        "limit": 10
    }
    headers = {"Accept": "application/json;version=20230302"}
    
    print(f"Fetching OHLCV minute candles for WAVAX/USDC pool {pool_address}...")
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            ohlcv_list = data.get("data", {}).get("attributes", {}).get("ohlcv_list", [])
            print(f"Fetched {len(ohlcv_list)} candles:")
            for c in ohlcv_list[:5]:
                print(f"  - {c}")
        else:
            print("Failed to fetch candles:", response.text)
    except Exception as e:
        print("Error occurred:", e)

if __name__ == "__main__":
    main()
