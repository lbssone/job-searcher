from flask import Flask, request, render_template, url_for, redirect
from flask_paginate import Pagination, get_page_args
import requests
from pyquery import PyQuery as pq
import json
from area import area_104, area_1111, area_518, area_dict
from job import jobcat_104, jobcat_1111, jobcat_518
from data import worktime_104, worktime_1111, worktime_518, salarytype_104, salarytype_1111, salarytype_518

app = Flask(__name__)
job_list = []
char_dict = {' ':'%20', '!':'%21', '"':'%22', '#':'%23', '$':'%24', '%':'%25', '&':'%26', '\'':'%27',
            '(':'%28', ')':'%29', '*':'%2A', '+':'%2B', ',':'%2C', '-':'%2D', '.':'%2E', '/':'%2F'}
keyword = ''
keyword_trans = ''
area_list = []
category_list = []
condition = ''
work_time = ''
salary_type = ''
salary = ''
interview_keyword = ''
search_history = {}


def get_job_list(offset=0, per_page=10):
    global job_list
    return job_list[offset: offset + per_page]

def get_key_word():
    global keyword
    return keyword


@app.route('/')
def index():
    return render_template('index.html', search_history=search_history, area_dict=area_dict, category_dict=jobcat_104 ,work_time_dict=worktime_104, salary_type_dict=salarytype_104)

@app.route('/search')
def search():
    global job_list, keyword, keyword_trans, area_list, category_list, condition, work_time, salary_type, salary, search_history
    job_list.clear()
    area_list.clear()
    category_list.clear()
    area_num_104, area_num_1111, area_num_518 = [] , [], []
    cat_num_104, cat_num_1111, cat_num_518 = [], [], []
    work_time_104, work_time_1111, work_time_518 = '', '', ''
    salary_type_104, salary_type_1111, salary_type_518 = '', '', ''

    keyword = request.values.get('keyword')
    area_list = request.values.getlist('area')
    try:
        for a in area_list:
            area_num_104.append(str(area_104[a]))
            area_num_1111.append(str(area_1111[a]))
            area_num_518.append(str(area_518[a]))
    except KeyError:
        area_list = []
        
    category_list = request.values.getlist('category')
    try:
        for c in category_list:
            cat_num_104.append(str(jobcat_104[c]))
            cat_num_1111.append(str(jobcat_1111[c]))
            cat_num_518.append(str(jobcat_518[c]))
    except KeyError:
        category_list = []

    work_time = request.values.get('work-time')
    if work_time:
        work_time_104 = worktime_104[work_time]
        work_time_1111 = worktime_1111[work_time]
        work_time_518 = worktime_518[work_time]
    else:
        work_time_104 = ''
        work_time_1111 = ''
        work_time_518 = ''
        
    salary_type = request.values.get('salary-type')
    if salary_type:
        salary_type_104 = salarytype_104[salary_type]
        salary_type_1111 = salarytype_1111[salary_type]
        salary_type_518 = salarytype_518[salary_type]
    else:
        salary_type_104 = ''
        salary_type_1111 = ''
        salary_type_518 = ''

    salary = request.values.get('salary')
    if salary == None:
        salary = ''

    for k in keyword:
        if k in char_dict:
            keyword_trans = keyword.replace(k, char_dict[k])
        else:
            keyword_trans = keyword
    if not keyword:
        keyword_trans = ''

    search_url = 'https://my-job-searcher.herokuapp.com/search?keyword={}&area={}&category={}&work-time={}&salary-type={}&salary={}'.format(keyword_trans, '&area'.join(area_list), '&category'.join(category_list), work_time, salary_type, salary)

    condition = keyword
    if area_list != []:
        condition += '+' + '+'.join(area_list)
    if category_list != []:
        condition += '+' + '+'.join(category_list)
    if work_time != '':
        condition += '+' + work_time
    if salary_type != '':
        condition += '+' + salary_type + salary

    search_history[condition] = search_url
    print('keyword: ' + keyword)
    print('keyword_trans: ' + keyword_trans)
    print('area_list:', area_list)
    print('category_list:', category_list)
    print('work_time: ' + work_time)
    print('salary: ' + salary)

    # 104
    # response_104 = requests.get('https://www.104.com.tw/jobs/search/?ro=0&kwop=7&keyword={}&order=14&asc=0&page=1&mode=s&jobsource=2018indexpoc'.format(keyword_trans))
    # doc_104 = pq(response_104.text)
    # total_page_104 = int(doc_104('#job-jobList > script:nth-child(14)').text().split('totalPage":')[1].split(',')[0])
    # for page_num in range(1, int((total_page_104+1)/10)):
    try:
        for page_num in range(1, 3):
            url = 'https://www.104.com.tw/jobs/search/?kwop=7&keyword={}&area={}&cat={}&ro={}&sctp={}&scmin={}&page={}&jobsource=2018indexpoc'.format(keyword_trans, ','.join(area_num_104), ','.join(cat_num_104), work_time_104, salary_type_104, salary, page_num)
            response = requests.get(url)
            doc = pq(response.text)
            jobs_doc = doc("#js-job-content article.b-block--top-bord.job-list-item.b-clearfix.js-job-item")
            for job_doc in jobs_doc.items():
                job_dict = {}
                job_dict['source'] = []
                source = {}
                source['site'] = '104人力銀行'
                source['link'] = job_doc('.js-job-link').attr('href')
                job_dict['source'].append(source)
                job_dict['title'] = job_doc('.js-job-link').text()
                job_dict['date'] = job_doc('.b-tit span.b-tit__date').text()
                job_dict['info'] = job_doc('.job-list-item__info').text()
                job_dict['company'] = {}
                job_dict['company']['name'] = job_doc('ul:nth-child(2) li:nth-child(2) a').text()
                job_dict['company']['link'] = job_doc('ul:nth-child(2) li:nth-child(2) a').attr('href')
                job_dict['area'] = job_doc('ul.b-list-inline.b-clearfix.job-list-intro.b-content li:nth-child(1)').text()
                job_dict['wage'] = job_doc('div.b-block__left > div > span:nth-child(1)')
                job_dict['experience'] = job_doc('ul.b-list-inline.b-clearfix.job-list-intro.b-content li:nth-child(3)').text()
                job_dict['education'] = job_doc('ul.b-list-inline.b-clearfix.job-list-intro.b-content li:nth-child(5)').text()            
                job_list.append(job_dict)
            print(salary)
            print('104 url: ' + url)
    except ConnectionError:
        print('104 connection error')
    # 1111
    try:
        count = 1
        while count <= 2:
            if work_time == '兼職':
                response_1111 = requests.get('https://www.1111.com.tw/job-bank/job-index.asp?tt=2,4&ks={}&c0={}&d0={}&ts={}&st={}&sa0={}&page={}&si=1'.format(keyword_trans, ','.join(area_num_1111), ','.join(cat_num_1111), work_time_1111, salary_type_1111, salary, count))
            elif work_time == '全職':
                response_1111 = requests.get('https://www.1111.com.tw/job-bank/job-index.asp?tt=1&ks={}&c0={}&d0={}&ts={}&st={}&sa0={}&page={}&si=1'.format(keyword_trans, ','.join(area_num_1111), ','.join(cat_num_1111), work_time_1111, salary_type_1111, salary, count))
            else:
                response_1111 = requests.get('https://www.1111.com.tw/job-bank/job-index.asp?ks={}&c0={}&d0={}&ts={}&st={}&sa0={}&page={}&si=1'.format(keyword_trans, ','.join(area_num_1111), ','.join(cat_num_1111), work_time_1111, salary_type_1111, salary, count))
            doc = pq(response_1111.text)
            jobs_doc = doc('#jobResult #record_{} li.digest'.format(count))
            for job_doc in jobs_doc.items():
                site = '1111人力銀行'
                title = job_doc('.jbInfoin h3 a').text()
                link = job_doc('.jbInfoin h3 a').attr('href')
                date = job_doc('.jbControl .date').text()
                info = job_doc('.jbInfoTxt p').text()
                company_name = job_doc('.jbInfoin h4 a').text()
                company_link = job_doc('.jbInfoin h4 a').attr('href')
                area = job_doc('.jbControl .location a').text()
                wage = job_doc('.needs').text().split('|')[0]
                experience = job_doc('.needs').text().split('|')[1]
                education = job_doc('.needs').text().split('|')[2]
                exist = False
                for job in job_list:
                    if job['title'] == title and job['company']['name'] == company_name and job['area'] == area:
                        source_list = []
                        for source in job['source']:
                            source_list.append(source['site'])
                        if site not in source_list:
                            new_source = {}
                            new_source['site'] = site
                            new_source['link'] = link
                            job['source'].append(new_source)
                        exist = True
                        break
                if exist == False:
                    job_dict = {}
                    job_dict['source'] = []
                    source = {}
                    source['site'] = site
                    source['link'] = link
                    job_dict['source'].append(source)
                    job_dict['title'] = title
                    job_dict['date'] = date
                    job_dict['info'] = info
                    job_dict['company'] = {}
                    job_dict['company']['name'] = company_name
                    job_dict['company']['link'] = company_link
                    job_dict['area'] = area
                    job_dict['wage'] = wage
                    job_dict['experience'] = experience
                    job_dict['education'] = education            
                    job_list.append(job_dict)
            print(salary)
            print(response_1111.url)
            next_page_link = doc("#PageFooterD .pagination a.active").parent().next().children().attr("href")
            if next_page_link:
                response_1111 = requests.get('https://www.1111.com.tw/job-bank/job-index.asp' + next_page_link)
                count += 1
            else:
                break
    except ConnectionError:
        print('1111 connection error')    
    
    # 518
    # response_518 = requests.get('https://www.518.com.tw/job-index-P-1.html?ad={}&aa={}%2C&ab={}%2C&ai={}&ak={}&ak_min={}'.format(keyword_trans, ','.join(area_num_518), ','.join(cat_num_518), work_time_518, salary_type_num, salary_num))
    # doc_518 = pq(response_518.text)
    # total_page_518 = int(doc_518('#linkpage span.pagecountnum').text().split(' / ')[-1])
    # try:
    #     for page_num in range(1, 4):
    #         url = 'https://www.518.com.tw/job-index-P-{}.html?ad={}&aa={}%2C&ab={}%2C&ai={}&ak={}&ak_min={}'.format(page_num, keyword_trans, ','.join(area_num_518), ','.join(cat_num_518), work_time_518, salary_type_518, salary)
    #         response_518 = requests.get(url)
    #         doc = pq(response_518.text)
    #         jobs_doc = doc("#listContent ul")
    #         for job_doc in jobs_doc.items():
    #             site = '518人力銀行'
    #             title = job_doc('.title a').text()
    #             link = job_doc('.title a').attr('href')
    #             date = job_doc('.date').text()
    #             info = job_doc('.sumbox p:nth-child(2)').text()
    #             company_name = job_doc('.company a').text()
    #             company_link = job_doc('.company a').attr('href')
    #             area = job_doc('.area').text().replace('-', '')
    #             wage = job_doc('.sumbox p:nth-child(1)').text()
    #             experience = job_doc('.exp').text()
    #             education = job_doc('.edu').text().split('/ ')[-1]
    #             exist = False
    #             for job in job_list:
    #                 if job['title'] == title and job['company']['name'] == company_name and job['area'] == area:
    #                     source_list = []
    #                     for source in job['source']:
    #                         source_list.append(source['site'])
    #                     if site not in source_list:
    #                         new_source = {}
    #                         new_source['site'] = site
    #                         new_source['link'] = link
    #                         job['source'].append(new_source)
    #                     exist = True
    #                     break
    #             if exist == False:
    #                 job_dict = {}
    #                 job_dict['source'] = []
    #                 source = {}
    #                 source['site'] = site
    #                 source['link'] = link
    #                 job_dict['source'].append(source)
    #                 job_dict['title'] = title
    #                 job_dict['date'] = date
    #                 job_dict['info'] = info
    #                 job_dict['company'] = {}
    #                 job_dict['company']['name'] = company_name
    #                 job_dict['company']['link'] = company_link
    #                 job_dict['area'] = area
    #                 job_dict['wage'] = wage
    #                 job_dict['experience'] = experience
    #                 job_dict['education'] = education        
    #                 job_list.append(job_dict)
    #         print(salary)
    #         print('518 url: ' + url)
    # except ConnectionError:
    #     print('518 connection error')

    
    print('length of job_list:', len(job_list))
    print('search history:', search_history)
    print('[redirect to /results]')
    return redirect(url_for('results'))


@app.route('/results')
def results():
    page, per_page, offset = get_page_args(page_parameter='page',
                                    per_page_parameter='per_page')
    total = len(job_list)
    pagination_job_list = get_job_list(offset=offset, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')
    keyword = get_key_word()
    print('[redirected]')
    return render_template('results.html', 
                            keyword=keyword, 
                            keyword_trans=keyword_trans,
                            area_list=area_list,
                            area_dict=area_dict,
                            category_list=category_list,
                            category_dict=jobcat_104,
                            condition=condition,
                            work_time=work_time,
                            work_time_dict=worktime_104,
                            salary_type=salary_type,
                            salary=salary,
                            salary_type_dict=salarytype_104,
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

@app.route('/test')
def test():
    return render_template('examination.html')

@app.route('/resume')
def resume():
    return render_template('resume.html')

if __name__ == "__main__":
    app.run(port=5000, debug = True)