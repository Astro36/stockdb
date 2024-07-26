import requests
from tqdm import tqdm


def main():
    r = requests.get("http://127.0.0.1:8000/symbols")
    data = r.json()
    for yfsymbol in tqdm(data):
        r = requests.get(f"http://127.0.0.1:8000/quotes/{yfsymbol}")
        if r.status_code == 404:
            continue
        if r.status_code != 200:
            print(yfsymbol)
            break


if __name__ == "__main__":
    main()
