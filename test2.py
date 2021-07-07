import re 

s = 'https://chisenowa.com/（ホームページ）'

url = re.search(r"https?://[\w!\?/\+\-_~=;\.,\*&@#\$%\(\)'\[\]]+", s).group()
print(url)