from flask import Flask, request, render_template, url_for
import requests
from pyquery import PyQuery as pq

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        keyword = request.values['keyword']
        response = requests.get('https://www.104.com.tw/jobs/search/?keyword=' + keyword + '&jobsource=2018indexpoc&ro=0&order=1')
        doc = pq(response.text)
        jobs_doc = doc("#js-job-content article.job-list-item")
        job_list = []
        for job_doc in jobs_doc.items():
            job_dict = {}
            job_dict['title'] = job_doc('.js-job-link').text()
            job_dict['link'] = job_doc('.js-job-link').attr('href')
            job_dict['info'] = job_doc('.job-list-item__info').text()
            job_list.append(job_dict)
        return render_template('index.html', keyword=keyword, job_list=job_list)



if __name__ == "__main__":
    app.run(debug = True)