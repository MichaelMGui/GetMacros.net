"""Metadata-only cost investigation; never downloads a dataset body."""
from datetime import datetime, timezone
import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import off_expand as off

TARGETS = {
    'official-daily-jsonl': 'https://static.openfoodfacts.org/data/openfoodfacts-products.jsonl.gz',
    'official-linked-hf-parquet': 'https://huggingface.co/datasets/openfoodfacts/product-database/resolve/main/food.parquet',
}


def main():
    results = {}
    wanted = ['content-length', 'content-type', 'last-modified', 'etag', 'accept-ranges', 'x-linked-size', 'x-linked-etag', 'x-repo-commit']
    for name, url in TARGETS.items():
        request = Request(url, method='HEAD', headers={'User-Agent': 'GetMacros-CoverageResearch/1.0 (https://getmacros.net/contact.html)', 'Accept-Encoding': 'identity'})
        try:
            with urlopen(request, timeout=20) as response:
                results[name] = {'url': url, 'status': response.status, 'headers': {key: response.headers.get(key) for key in wanted if response.headers.get(key)}, 'responseBodyBytesRead': 0}
        except (HTTPError, URLError, TimeoutError, OSError) as error:
            results[name] = {'url': url, 'errorType': type(error).__name__,
                             'httpStatus': error.code if isinstance(error, HTTPError) else None,
                             'error': 'Outbound metadata request unavailable in this sandbox; no dataset was downloaded.', 'responseBodyBytesRead': 0}
    evidence = {'checkedAt': datetime.now(timezone.utc).isoformat(), 'requestPolicy': 'Two HTTP HEAD requests only. No dataset body read, no extraction, no product API calls.', 'results': results}
    off.dump(off.OUT / 'off-download-metadata.json', evidence)
    print(json.dumps(evidence, indent=2), flush=True)


if __name__ == '__main__':
    main()
