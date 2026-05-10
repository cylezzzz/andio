import requests

class DownloadManager:
    def download(self, url, output_path):
        response = requests.get(url, stream=True)

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(8192):
                f.write(chunk)
