import pandas as pd
import matplotlib.pyplot as plt
import urllib.request
from bs4 import BeautifulSoup

# 한글 폰트 설정 (예: 맑은 고딕 사용)
plt.rc('font', family='Malgun Gothic')

# 저장할 데이터를 담을 리스트
Yestwo_stores = list()

# 크롤링할 페이지 범위 설정 (1부터 10페이지까지)
for page in range(1, 11):
    Yestwo_url = f"https://www.yes24.com/24/Category/Display/001001046003?PageNumber={page}"
    # print(f"Crawling URL: {Yestwo_url}")

    try:
        html = urllib.request.urlopen(Yestwo_url)
        soup = BeautifulSoup(html, 'html.parser')
        main_content = soup.find('div', {'id': 'category_layout'})

        for item in main_content.find_all('li'):
            try:
                book_name = item.find('div', {'class': 'goods_name'}).find('a').text.strip()
                author_info = item.find('span', {'class': 'goods_auth'}).text.strip()
                publisher = item.find('span', {'class': 'goods_pub'}).text.strip()
                rating = float(item.find('span', {'class': 'gd_rating'}).find('em', {'class': 'yes_b'}).text.strip())
                review_count = int(
                    item.find('span', {'class': 'gd_reviewCount'}).find('em').text.strip().replace(",", ""))
                Yestwo_stores.append([book_name, author_info, publisher, rating, review_count])
            except AttributeError:
                continue
    except Exception as e:
        print(f"Error fetching {Yestwo_url}: {e}")

# 크롤링 결과 출력
print(f"RESULT of Crawling : \r\n{Yestwo_stores}")

# 데이터프레임 생성 및 파일 저장
if Yestwo_stores:
    df = pd.DataFrame(Yestwo_stores, columns=['도서명', '저자 정보', '출판사', '평점', '회원리뷰수'])
    df.to_csv("./Yestwo_table.csv", encoding='utf-8', index=False)
    df.to_excel("./Yestwo_table_new.xlsx", index=False, engine='openpyxl')

    # 평점 상위 50권 막대 그래프
    plt.figure(figsize=(12, 8))
    top_books_by_rating = df.nlargest(50, '평점')
    plt.barh(top_books_by_rating['도서명'], top_books_by_rating['평점'], edgecolor='black')
    plt.xlabel('평점')
    plt.ylabel('도서명')
    plt.title('Top 50 도서 평점 비교')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.show()

    # 리뷰 수와 평점의 상관관계 산점도
    plt.figure(figsize=(10, 6))
    plt.scatter(df['회원리뷰수'], df['평점'], alpha=0.6)
    plt.xlabel('회원리뷰수')
    plt.ylabel('평점')
    plt.title('리뷰수와 평점의 상관관계')
    plt.tight_layout()
    plt.show()


    # 회원리뷰수 상위 50권 막대 그래프
    plt.figure(figsize=(12, 8))
    top_books_by_review_count = df.nlargest(50, '회원리뷰수')
    plt.barh(top_books_by_review_count['도서명'], top_books_by_review_count['회원리뷰수'], edgecolor='black')
    plt.xlabel('회원리뷰수')
    plt.ylabel('도서명')
    plt.title('Top 50 도서 회원리뷰수 비교')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.show()

    # 작가별 리뷰수 집계 및 그래프
    author_review_count = df.groupby('저자 정보')['회원리뷰수'].sum().reset_index().sort_values(by='회원리뷰수', ascending=False)
    plt.figure(figsize=(12, 8))
    top_authors = author_review_count.head(10)
    plt.barh(top_authors['저자 정보'], top_authors['회원리뷰수'], edgecolor='black')
    plt.xlabel('회원리뷰수')
    plt.ylabel('작가')
    plt.title('Top 10 작가별 회원리뷰수 비교')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.show()

else:
    print("저장할 데이터가 없습니다.")