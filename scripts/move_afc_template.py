import mwclient
import time
import re
import os

def login_to_site(api_url, api_path, username, password, user_agent):
    try:
        # 登录到MediaWiki站点
        site = mwclient.Site(api_url, path=api_path, clients_useragent=user_agent)
        site.login(username, password)
        print("登录成功")
        return site
    except mwclient.errors.LoginError as e:
        print(f"登录失败: {e}")
        return None
    except mwclient.errors.InvalidResponse as e:
        print(f"无效响应: {e}")
        return None
    except Exception as e:
        print(f"发生未知错误: {e}")
        return None

def get_all_pages_in_categories(site, categories):
    pages = []
    for category_name in categories:
        try:
            print(f"正在获取分类 '{category_name}' 中的页面...")
            category = site.categories[category_name]
            for page in category:
                pages.append(page)
        except Exception as e:
            print(f"获取分类 '{category_name}' 页面时发生错误: {e}")
    return pages

def check_and_update_drafts(site, categories):
    if not site:
        print("由于登录失败，无法检查和更新草稿页面")
        return
    try:
        # 获取分类中的页面
        pages = get_all_pages_in_categories(site, categories)
        print(f"获取到 {len(pages)} 个页面")
        
        # 标志位，表示是否有页面被处理
        pages_processed = False
        
        for page in pages:
            print(f"页面: {page.name}"
        
        time.sleep(1.5)
        
        # 正则表达式匹配{{AFC submission}}模板
        afc_template_pattern = re.compile(r'{{AFC submission.*?}}', re.DOTALL)
        
        for page in pages:
            try:
                print(f"正在处理页面: {page.name}")
                
                # 获取草稿页面文本
                draft_page_text = page.text()
                print(f"获取到页面文本，长度: {len(draft_page_text)}")
                
                # 查找所有{{AFC submission}}模板
                afc_templates = afc_template_pattern.findall(draft_page_text)
                print(f"找到 {len(afc_templates)} 个{{AFC submission}}模板")
                
                if afc_templates:
                    # 储存最后一个{{AFC submission}}模板
                    last_afc_template = afc_templates[-1]
                    print(f"储存最后一个{{AFC submission}}模板: {last_afc_template}")
                    
                    # 移除所有{{AFC submission}}模板
                    new_text = afc_template_pattern.sub('', draft_page_text)
                    print("移除所有{{AFC submission}}模板")
                    
                    # 检查并移除页面顶部多余的空行，跳过带有注释的行
                    lines = new_text.split('\n')
                    content_start_index = 0
                    for i, line in enumerate(lines):
                        if line.strip() and not line.strip().startswith('<!--'):
                            content_start_index = i
                            break
                    new_text = '\n'.join(lines[content_start_index:])
                    print("移除页面顶部多余的空行")
                    
                    # 将最后一个{{AFC submission}}模板放在第一个有实际内容的行上方
                    new_text = last_afc_template + '\n' + new_text
                    print("将最后一个{{AFC submission}}模板放在页面最顶端")
                    
                    # 更新页面内容
                    page.save(new_text, summary='重构AFC模板位置')
                    print(f'已更新页面 {page.name} 的AFC模板位置')
                    
                    # 设置标志位为True
                    pages_processed = True
                else:
                    print(f'页面 {page.name} 不包含{{AFC submission}}模板，跳过')
                
                # 添加一至两秒的间隔
                time.sleep(1.5)
            except mwclient.errors.InvalidResponse as e:
                print(f"无效响应: {e}")
            except Exception as e:
                print(f"处理页面 {page.name} 时发生错误: {e}")

        if not pages_processed:
            print('没有页面需要处理，程序停止')
        else:
            print('任务完成')
    except mwclient.errors.InvalidResponse as e:
        print(f"无效响应: {e}")
    except Exception as e:
        print(f"获取分类页面时发生错误: {e}")

if __name__ == "__main__":
    try:
        # 从环境变量中读取敏感数据
        api_url = os.getenv('API_URL')
        api_path = os.getenv('API_PATH')
        user_agent = os.getenv('USER_AGENT')
        username = os.getenv('USERNAME')
        password = os.getenv('PASSWORD')
        categories = os.getenv('CATEGORIES').split(',')

        site = login_to_site(api_url, api_path, username, password, user_agent)
        check_and_update_drafts(site, categories)
    except KeyboardInterrupt:
        print("\n操作已被用户中断。")
