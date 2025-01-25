# import os
# from openai import OpenAI

# # 读取api_key
# file_path = os.path.abspath(__file__)
# file_path = os.path.dirname(file_path)
# try:
#     with open(f"{file_path}/deepseek.token", "r", encoding="utf-8") as f:
#         api_key = f.read()
#         if not api_key:
#             raise ValueError("No API key found in deepseek.token file.")
# except FileNotFoundError:
#     raise FileNotFoundError("deepseek.token file not found.")


# # 读取系统提示词
# system_prompt = ""
# with open(f"{file_path}/prompt.md", "r", encoding="utf-8") as f:
#     system_prompt = f.read()

# # 读取待处理的句子
# message_value = ""
# with open(f"{file_path}/test.txt", "r", encoding="utf-8") as f:
#     message_value = f.read()

# client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# response = client.chat.completions.create(
#     model="deepseek-coder",
#     messages=[
#         {"role": "system", "content": system_prompt},
#         {"role": "user", "content": message_value},
#     ],
#     max_tokens=8192,
#     temperature=0.7,
#     stream=False,
# )

# print(f"AI response: finish_reason: {response.choices[0].finish_reason}")
# print(f"AI response: model: {response.model}")
# print(f"AI response: usage: {response.usage}")
# print(response.choices[0].message.content)


import os
from openai import OpenAI

def group_sentences_to_paragraphs(message_value):
    # 读取api_key
    file_path = os.path.abspath(__file__)
    file_path = os.path.dirname(file_path)
    try:
        with open(f"{file_path}/deepseek.token", "r", encoding="utf-8") as f:
            api_key = f.read()
            if not api_key:
                raise ValueError("No API key found in deepseek.token file.")
    except FileNotFoundError:
        raise FileNotFoundError("deepseek.token file not found.")

    # 读取系统提示词
    system_prompt = ""
    with open(f"{file_path}/prompt.md", "r", encoding="utf-8") as f:
        system_prompt = f.read()

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    response = client.chat.completions.create(
        model="deepseek-coder",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message_value},
        ],
        max_tokens=8192,
        temperature=0.7,
        stream=False,
    )

    print(f"AI response: finish_reason: {response.choices[0].finish_reason}")
    print(f"AI response: model: {response.model}")
    print(f"AI response: usage: {response.usage}")
    return response.choices[0].message.content

# 示例调用
if __name__ == "__main__":
    # 读取待处理的句子
    file_path = os.path.abspath(__file__)
    file_path = os.path.dirname(file_path)
    message_value = ""
    with open(f"{file_path}/test.txt", "r", encoding="utf-8") as f:
        message_value = f.read()

    ai_response = group_sentences_to_paragraphs(message_value)
    print(ai_response)