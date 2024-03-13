import io
import re
import base64
import requests
from pdf2image import convert_from_bytes

def convert_pdf_to_base64_images(file_content):
    pages = convert_from_bytes(file_content)
    
    base64_images = []
    for page in pages:
        with io.BytesIO() as output:
            page.save(output, format='JPEG')
            base64_image = base64.b64encode(output.getvalue()).decode('utf-8')
            base64_images.append(base64_image)
    return base64_images


def openai_api_call(base64_images):
    api_key = "YOUR_API_KEY"
    
    prompt = "Can you fill in the blanks? 'Name of account holder: ____________ Total portfolio value: ____________.' and can you list the name and the total cost basis of each holding in this format? 'Holding name: ____________ Cost basis: ____________'. This information is included on pages with the heading 'Holdings'. The name is under the 'description' column and the cost basis is under the 'total cost basis' column."
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": prompt
                }
            ]
            }
        ],
        "max_tokens": 500
    }
    
    for base64_image in base64_images:
        payload["messages"][0]["content"].append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
        })
        
    return requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)


def parse_response(response_json):
    response_text = response_json["choices"][0]["message"]["content"]
    
    name_match = re.search(r'Name of account holder: (.+)\n', response_text)
    if name_match:
        account_holder_name = name_match.group(1)
    else:
        raise ValueError("Name of account holder not found in response")
    
    portfolio_value_match = re.search(r'Total portfolio value: (\$\d+(?:,\d{3})*(?:\.\d{2})?)\n', response_text)
    if portfolio_value_match:
        portfolio_value = portfolio_value_match.group(1)
    else:
        raise ValueError("Total portfolio value not found in response")
    
    holdings = re.findall(r'Holding name: (.+)\nCost basis: (.+)\n', response_text)
    holdings_dict = {holding[0]: holding[1] for holding in holdings}
    
    return (account_holder_name, portfolio_value, holdings_dict)