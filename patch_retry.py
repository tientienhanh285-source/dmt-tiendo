import sys

def main():
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix single scan
    old_single = """                                        else:
                                            # Ép temperature=0.0 để AI phân tích logic nhất quán (không bị sáng tạo ngẫu nhiên sau mỗi lần quét)
                                            response = model.generate_content(
                                                prompt, 
                                                generation_config={"temperature": 0.0},
                                                request_options={"retry": None, "timeout": 30.0}
                                            )
                                            raw_text = response.text
                                            with open(cache_file, "w", encoding="utf-8") as f:
                                                f.write(raw_text)"""
    new_single = """                                        else:
                                            max_retries = 3
                                            for attempt in range(max_retries):
                                                try:
                                                    response = model.generate_content(
                                                        prompt, 
                                                        generation_config={"temperature": 0.0},
                                                        request_options={"timeout": 60.0}
                                                    )
                                                    raw_text = response.text
                                                    break
                                                except Exception as api_err:
                                                    if attempt == max_retries - 1:
                                                        raise api_err
                                                    import time
                                                    time.sleep(4 * (attempt + 1))
                                                    
                                            if raw_text:
                                                with open(cache_file, "w", encoding="utf-8") as f:
                                                    f.write(raw_text)"""
    
    if old_single in content:
        content = content.replace(old_single, new_single)
        print("Patched single scan.")
        
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    main()
