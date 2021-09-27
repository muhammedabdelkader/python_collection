import json, requests

class http_requests:

        def send_http_request(
            url, http_headers, data, return_key, json_data=True, post_request=True
        ):
            """Execute POST/GET HTTP method sending DATA/JSON formate"""
            try:
                if post_request:
                    # Send POST request
                    if json_data:
                        response = requests.post(
                            url=url, headers=http_headers, json=data
                        )
                    else:
                        response = requests.post(
                            url=url, headers=http_headers, data=data
                        )
                else:
                    # Send GET request
                    if json_data:
                        response = requests.get(
                            url=url, headers=http_headers, json=data
                        )
                    else:
                        response = requests.get(
                            url=url, headers=http_headers, data=data
                        )
                if response.status_code == 200:
                    return response.json().get(return_key, 0)
                else:
                    raise ValueError(
                        f"Connection to {url} gives http code {response.status_code}"
                    )
            except Exception as err:
                print(f"Other error occurred: {err}")
