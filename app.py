from flask import Flask, request, render_template, url_for, redirect
from flask_paginate import Pagination, get_page_args
import requests
from pyquery import PyQuery as pq
import json
from area import area_dict
from data import work_time_dict, salary_dict

app = Flask(__name__)
job_list = []
char_dict = {' ':'%20', '!':'%21', '"':'%22', '#':'%23', '$':'%24', '%':'%25', '&':'%26', '\'':'%27',
            '(':'%28', ')':'%29', '*':'%2A', '+':'%2B', ',':'%2C', '-':'%2D', '.':'%2E', '/':'%2F'}
keyword = ''
keyword_trans = ''
area_list = []
area_num_list = []
category = ''
work_time = ''
work_time_num = ''
salary = ''
salary_num = ''
interview_keyword = ''
search_history = {}


def get_job_list(offset=0, per_page=10):
    return job_list[offset: offset + per_page]

def get_key_word():
    return keyword


@app.route('/')
def index():
    return render_template('index.html', search_history=search_history, area_dict=area_dict, work_time_dict=work_time_dict, salary_dict=salary_dict)

@app.route('/search')
def search():
    global job_list, keyword, keyword_trans, area_list, area_num_list, category, work_time,salary
    job_list.clear()
    area_list.clear()
    area_num_list.clear()
    keyword = request.values.get('keyword')
    area_list = request.values.getlist('area')
    for a in area_list:
        area_num_list.append(area_dict[a])
    category = request.values.get('category')
    work_time = request.values.get('work-time')
    if work_time:
        work_time_num = work_time_dict[work_time]
    else:
        work_time_num = ''
    salary = request.values.get('salary')
    if salary:
        salary_num = salary_dict[salary]
    else:
        salary_num = ''
    for k in keyword:
        if k in char_dict:
            keyword_trans = keyword.replace(k, char_dict[k])
        else:
            keyword_trans = keyword
    if not keyword:
        keyword_trans = ''

    search_url = 'http://127.0.0.1:5000/search?keyword={}&area={}&category={}&work-time={}&salary={}'.format(keyword_trans, '&area'.join(area_list), category, work_time, salary)
    # search_url = 'http://127.0.0.1:5000/search?keyword=' + keyword_trans

    condition = keyword
    if area_num_list:
        condition += '+' + '+'.join(area_list)
    if category:
        condition += '+' + category
    if work_time:
        condition += '+' + work_time
    if salary:
        condition += '+' + salary
        # search_url = '{}&area={}'.format(search_url, '&area='.join(area_list))
    if category:
        search_url = '{}&category={}'.format(search_url, category)
    search_history[condition] = search_url
    # 104
    # response_104 = requests.get('https://www.104.com.tw/jobs/search/?ro=0&kwop=7&keyword={}&order=14&asc=0&page=1&mode=s&jobsource=2018indexpoc'.format(keyword_trans))
    # doc_104 = pq(response_104.text)
    # total_page_104 = int(doc_104('#job-jobList > script:nth-child(14)').text().split('totalPage":')[1].split(',')[0])
    # job_list = []
    # for page_num in range(1, int((total_page_104+1)/10)):
    for page_num in range(1, 5):
        url = 'https://www.104.com.tw/jobs/search/?ro=0&kwop=7&keyword={}&area={}&cat={}&ro={}&scmin={}&page={}&jobsource=2018indexpoc'.format(keyword_trans, ','.join(area_num_list), category, work_time_num, salary_num, page_num)
        response = requests.get(url)
        doc = pq(response.text)
        jobs_doc = doc("#js-job-content article.job-list-item")
        for job_doc in jobs_doc.items():
            job_dict = {}
            job_dict['source'] = '104人力銀行'
            job_dict['title'] = job_doc('.js-job-link').text()
            job_dict['link'] = job_doc('.js-job-link').attr('href')
            job_dict['date'] = job_doc('.b-tit span.b-tit__date').text()
            job_dict['info'] = job_doc('.job-list-item__info').text()
            job_dict['company'] = {}
            job_dict['company']['name'] = job_doc('ul:nth-child(2) li:nth-child(2) a').text()
            job_dict['company']['link'] = job_doc('ul:nth-child(2) li:nth-child(2) a').attr('href')
            job_dict['area'] = job_doc('ul.b-list-inline.b-clearfix.job-list-intro.b-content li:nth-child(1)').text()
            job_dict['salary'] = job_doc('div.b-block__left > div > span:nth-child(1)')
            job_dict['experience'] = job_doc('ul.b-list-inline.b-clearfix.job-list-intro.b-content li:nth-child(3)').text()
            job_dict['education'] = job_doc('ul.b-list-inline.b-clearfix.job-list-intro.b-content li:nth-child(5)').text()            
            job_list.append(job_dict)
    # 1111
    count = 0
    while count <= 5:
        response_1111 = requests.get('https://www.1111.com.tw/job-bank/job-index.asp?si=1&ss=s&ks={}&page={}'.format(keyword_trans, count))
        doc = pq(response_1111.text)
        jobs_doc = doc('#jobResult #record_{} li.digest'.format(count))
        for job_doc in jobs_doc.items():
            source = '1111人力銀行'
            title = job_doc('.jbInfoin h3 a').text()
            link = job_doc('.jbInfoin h3 a').attr('href')
            date = job_doc('.jbControl .date').text()
            info = job_doc('.jbInfoTxt p').text()
            company_name = job_doc('.jbInfoin h4 a').text()
            company_link = job_doc('.jbInfoin h4 a').attr('href')
            area = job_doc('.jbControl .location a').text()
            salary = job_doc('.needs').text().split('|')[0]
            experience = job_doc('.needs').text().split('|')[1]
            education = job_doc('.needs').text().split('|')[2]
            exist = False
            for job in job_list:
                if job['title'] == title and job['company']['name'] == company_name and job['area'] == area:
                    job['source'] += ' ' + source
                    job['link'] += ' ' + link
                    exist = True
                    break
            if not exist:
                job_dict = {}
                job_dict['source'] = source
                job_dict['title'] = title
                job_dict['link'] = link
                job_dict['date'] = date
                job_dict['info'] = info
                job_dict['company'] = {}
                job_dict['company']['name'] = company_name
                job_dict['company']['link'] = company_link
                job_dict['area'] = area
                job_dict['salary'] = salary
                job_dict['experience'] = experience
                job_dict['education'] = education            
                job_list.append(job_dict)
        next_page_link = doc("#PageFooterD .pagination a.active").parent().next().children().attr("href")
        if next_page_link:
            response_1111 = requests.get('https://www.1111.com.tw/job-bank/job-index.asp' + next_page_link)
            count += 1
        else:
            break
    
    # 518
    response_518 = requests.get('https://www.518.com.tw/job-index.html?ad={}&aa=&ab=2032001&ac=&am=&i='.format(keyword_trans))
    doc_518 = pq(response_518.text)
    total_page_518 = int(doc_518('#linkpage span.pagecountnum').text().split(' / ')[-1])
    for page_num in range(1, total_page_518+1):
        url = 'https://www.518.com.tw/job-index-P-{}.html?i=1&am=1&ab=2032001,&ad={}'.format(page_num, keyword_trans)
        response = requests.get(url)
        doc = pq(response.text)
        jobs_doc = doc("#listContent ul")
        for job_doc in jobs_doc.items():
            source = '518人力銀行'
            title = job_doc('.title a').text()
            link = job_doc('.title a').attr('href')
            date = job_doc('.date').text()
            info = job_doc('.sumbox p:nth-child(2)').text()
            company_name = job_doc('.company a').text()
            company_link = job_doc('.company a').attr('href')
            area = job_doc('.area').text().replace('-', '')
            salary = job_doc('.sumbox p:nth-child(1)').text()
            experience = job_doc('.exp').text()
            education = job_doc('.edu').text().split('/ ')[-1]
            exist = False
            for job in job_list:
                if job['title'] == title and job['company']['name'] == company_name and job['area'] == area:
                    job['source'] += ' ' + source
                    job['link'] += ' ' + link
                    exist = True
                    break
            if not exist:
                job_dict = {}
                job_dict['source'] = source
                job_dict['title'] = title
                job_dict['link'] = link
                job_dict['date'] = date
                job_dict['info'] = info
                job_dict['company'] = {}
                job_dict['company']['name'] = company_name
                job_dict['company']['link'] = company_link
                job_dict['area'] = area
                job_dict['salary'] = salary
                job_dict['experience'] = experience
                job_dict['education'] = education        
                job_list.append(job_dict)
    
    print(len(job_list))
    print(area_num_list)
    print(search_history)
    return redirect(url_for('results'))
    # return render_template('index.html')


@app.route('/results')
def results():
    page, per_page, offset = get_page_args(page_parameter='page',
                                    per_page_parameter='per_page')
    total = len(job_list)
    pagination_job_list = get_job_list(offset=offset, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')
    keyword = get_key_word()
    print('keyword: ' + keyword)
    print('keyword_trans: ' + keyword_trans)
    return render_template('index.html', 
                            keyword=keyword, 
                            keyword_trans=keyword_trans,
                            area_list=area_list,
                            area_dict=area_dict,
                            category=category,
                            work_time=work_time,
                            work_time_dict=work_time_dict,
                            salary=salary,
                            salary_dict=salary_dict,
                            job_list=pagination_job_list,
                            search_history=search_history,
                            page=page,
                            per_page=per_page,
                            pagination=pagination)

@app.route('/interview', methods=['GET', 'POST'])
def interview():
    if request.method == 'GET':
        return render_template('interview_results.html')
    elif request.method == 'POST':
        interview_list = []
        btn_query = request.values.get('interview-btn')
        # global keyword_trans
        # keyword_trans
        api_key = 'AIzaSyAjbXA-q2exro1mvZAGejN_QJ53JuH0O44'
        cx = '008688161330259078405:trwkkultef8'
        if btn_query:
            url = 'https://www.googleapis.com/customsearch/v1?key={}&cx={}&lr=lang_zh-TW&q={}%20面試'.format(api_key, cx, btn_query)
        else:
            global interview_keyword
            interview_keyword = request.values.get('interview-keyword')
            url = 'https://www.googleapis.com/customsearch/v1?key={}&cx={}&lr=lang_zh-TW&q={}%20面試'.format(api_key, cx, interview_keyword)
        response = requests.get(url)
        data = json.loads(response.text)
        interview_results = data['items']
        for interview in interview_results:
            interview_dict = {}
            interview_dict['title'] = interview['title']
            interview_dict['link'] = interview['link']
            snippet = interview['snippet'].split(' ... ')
            if len(snippet) > 1:
                interview_dict['date'] = snippet[0]
                interview_dict['snippet'] = snippet[1]
            else:
                interview_dict['snippet'] = snippet[0]
            # interview_dict['full_description'] = interview['pagemap']['metatags'][0]['og:description']
            interview_list.append(interview_dict)
        print(url)
        if btn_query:
            return render_template('interview_results.html', interview_list=interview_list, keyword=keyword)
        elif interview_keyword:
            return render_template('interview_results.html', interview_list=interview_list, interview_keyword=interview_keyword)
        else:
            return render_template('interview_results.html', interview_list=interview_list)




if __name__ == "__main__":
    app.run(port=5000, debug = True)