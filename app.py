from flask import Flask, request, render_template, url_for, redirect
from flask_paginate import Pagination, get_page_args
import requests
from pyquery import PyQuery as pq

app = Flask(__name__)
job_list = []
char_dict = {' ':'%20', '!':'%21', '"':'%22', '#':'%23', '$':'%24', '%':'%25', '&':'%26', '\'':'%27',
            '(':'%28', ')':'%29', '*':'%2A', '+':'%2B', ',':'%2C', '-':'%2D', '.':'%2E', '/':'%2F'}
keyword = ''
search_history = {}


def get_job_list(offset=0, per_page=10):
    return job_list[offset: offset + per_page]

def get_key_word():
    return keyword


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method =='POST':
        job_list.clear()
        global keyword
        keyword = request.values.get('keyword')
        region = request.values.getlist('region')
        for k in keyword:
            if k in char_dict:
                keyword_trans = keyword.replace(k, char_dict[k])
            else:
                keyword_trans = keyword
        if not keyword:
            keyword_trans = ''
        if region:
            condition = keyword + '+' + '+'.join(region)
        else:
            condition = keyword
        # search_history[condition] = 
        # 104
        # response_104 = requests.get('https://www.104.com.tw/jobs/search/?ro=0&kwop=7&keyword={}&order=14&asc=0&page=1&mode=s&jobsource=2018indexpoc'.format(keyword_trans))
        # doc_104 = pq(response_104.text)
        # total_page_104 = int(doc_104('#job-jobList > script:nth-child(14)').text().split('totalPage":')[1].split(',')[0])
        # job_list = []
        # for page_num in range(1, int((total_page_104+1)/10)):
        for page_num in range(1, 5):
            url = 'https://www.104.com.tw/jobs/search/?ro=0&kwop=7&keyword={}&order=14&asc=0&page={}&mode=s&jobsource=2018indexpoc'.format(keyword_trans, page_num)
            response = requests.get(url)
            doc = pq(response.text)
            jobs_doc = doc("#js-job-content article.job-list-item")
            for job_doc in jobs_doc.items():
                job_dict = {}
                job_dict['title'] = job_doc('.js-job-link').text()
                job_dict['link'] = job_doc('.js-job-link').attr('href')
                job_dict['date'] = job_doc('.b-tit span.b-tit__date').text()
                job_dict['info'] = job_doc('.job-list-item__info').text()
                job_dict['company'] = {}
                job_dict['company']['name'] = job_doc('ul:nth-child(2) li:nth-child(2) a').text()
                job_dict['company']['link'] = job_doc('ul:nth-child(2) li:nth-child(2) a').attr('href')
                job_dict['region'] = job_doc('ul.b-list-inline.b-clearfix.job-list-intro.b-content li:nth-child(1)').text()
                job_dict['salary'] = job_doc('div.b-block__left > div > span:nth-child(1)')
                job_dict['experience'] = job_doc('ul.b-list-inline.b-clearfix.job-list-intro.b-content li:nth-child(3)').text()
                job_dict['education'] = job_doc('ul.b-list-inline.b-clearfix.job-list-intro.b-content li:nth-child(5)').text()            
                job_list.append(job_dict)
        # 1111
        # response_1111 = requests.get('https://www.1111.com.tw/job-bank/job-index.asp?si=1&ss=s&ks={}&page=1'.format(keyword))
        # count = 0
        # while count < 5:
        #     doc = pq(response_1111.text)
        #     jobs_doc = doc('#jobResult #record_1 li.digest')
        #     for job_doc in jobs_doc.items():
        #         job_dict = {}
        #         job_dict['title'] = job_doc('.jbInfoin h3 a').text()
        #         job_dict['link'] = job_doc('.jbInfoin h3 a').attr('href')
        #         job_dict['date'] = job_doc('.jbControl .date').text()
        #         job_dict['info'] = job_doc('.jbInfoTxt p').text()
        #         job_dict['company'] = {}
        #         job_dict['company']['name'] = job_doc('.jbInfoin h4 a').text()
        #         job_dict['company']['link'] = job_doc('.jbInfoin h4 a').attr('href')
        #         job_dict['region'] = job_doc('.jbControl .location a').text()
        #         job_dict['salary'] = job_doc('.needs').text().split('|')[0]
        #         job_dict['experience'] = job_doc('.needs').text().split('|')[1]
        #         job_dict['education'] = job_doc('.needs').text().split('|')[2]            
        #         job_list.append(job_dict)
        #     next_page_link = doc("#PageFooterD .pagination a.active").parent().next().children().attr("href")
        #     if next_page_link:
        #         response = requests.get('https://www.1111.com.tw/job-bank/job-index.asp' + next_page_link)
        #         count += 1
        #     else:
        #         break
        
        # # 518
        # response_518 = requests.get('https://www.518.com.tw/job-index.html?ad={}&aa=&ab=2032001&ac=&am=&i='.format(keyword))
        # doc_518 = pq(response_518.text)
        # total_page_518 = int(doc_518('#linkpage span.pagecountnum').text().split(' / ')[-1])
        # for page_num in range(1, total_page_518+1):
        #     url = 'https://www.518.com.tw/job-index-P-{}.html?i=1&am=1&ab=2032001,&ad={}'.format(page_num, keyword)
        #     response = requests.get(url)
        #     doc = pq(response.text)
        #     jobs_doc = doc("#listContent ul")
        #     for job_doc in jobs_doc.items():
        #         job_dict = {}
        #         job_dict['title'] = job_doc('.title a').text()
        #         job_dict['link'] = job_doc('.title a').attr('href')
        #         job_dict['date'] = job_doc('.date').text()
        #         job_dict['info'] = job_doc('.sumbox p:nth-child(2)').text()
        #         job_dict['company'] = {}
        #         job_dict['company']['name'] = job_doc('.company a').text()
        #         job_dict['company']['link'] = job_doc('.company a').attr('href')
        #         job_dict['region'] = job_doc('.area').text()
        #         job_dict['salary'] = job_doc('.sumbox p:nth-child(1)').text()
        #         job_dict['experience'] = job_doc('.exp').text()
        #         job_dict['education'] = job_doc('.edu').text().split('/ ')[-1]        
        #         job_list.append(job_dict)
        
        print(job_list)
        print(url)
        print(region)
        return redirect(url_for('results'))
    return render_template('index.html')


@app.route('/results')
def results():
    page, per_page, offset = get_page_args(page_parameter='page',
                                    per_page_parameter='per_page')
    total = len(job_list)
    pagination_job_list = get_job_list(offset=offset, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')
    keyword = get_key_word()
    print('results: ' + keyword)
    return render_template('index.html', keyword=keyword, job_list=pagination_job_list,
                           page=page,
                           per_page=per_page,
                           pagination=pagination)

if __name__ == "__main__":
    app.run(debug = True)