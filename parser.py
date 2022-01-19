import requests
from bs4 import BeautifulSoup as bs
from time import sleep, time
from db_map import DatabaseMapper
import re

start_time = time()
host = 'https://vstup.osvita.ua'


class Parser(DatabaseMapper):

    @staticmethod
    def get_areas():

        start_link = 'https://vstup.osvita.ua/spec/1-40-1/0-0-0-104-0-0/'
        result = requests.get(start_link).text
        soup = bs(result, 'html.parser')
        links_of_areas = []

        galuzi = soup.find("select", class_="galuz-select1", id="industryId")

        for option in galuzi.find_all('option'):
            if option['value'] != '0':
                links_of_areas.append({'name': option.text,
                                       'link': f'https://vstup.osvita.ua/spec/1-40-1/0-{option["value"]}-0-104-0-0',
                                       'code': option["value"]})
                DatabaseMapper().add_area(option.text, option['value'])
        Parser.get_specs(links_of_areas)
        print(f'=======FINISHED=======\n{time() - start_time} ')

    @staticmethod
    def courses_ln_gen(courses):

        course_links = []
        for link in courses:
            course_links.append(f'{host}{link.get("href")}')

        return course_links

    @staticmethod
    def get_specs(links_of_areas):

        for link in links_of_areas:
            result = requests.get(link['link']).text
            soup = bs(result, 'html.parser')
            courses = soup.findAll('a', class_='green-button')
            area_courses = {'area': link['code'],
                            'links': Parser.courses_ln_gen(courses)}

            for course in area_courses['links']:
                spec = dict()
                spec['area'] = area_courses['area']
                soup = bs(requests.get(course).text, 'html.parser')
                spec['name'] = soup.find(
                    'div', class_='page-vnz-detail-title').find('h1').findAll('b')[1].text
                spec['program'] = soup.find(
                    'div', class_='page-vnz-detail-title').find('h1').findAll('b')[0].text
                coefficients = Parser.get_coefficients(soup)
                try:
                    linkfordetails = soup.findAll(
                        'table', class_="stats-vnz-table")[0].find('a')
                except (KeyError, ValueError, IndexError):
                    continue

                links_f_details = f"{host}{linkfordetails.get('href')}"
                soup = bs(requests.get(links_f_details).text, 'html.parser')
                table = soup.find('table', class_="stats-vnz-table")

                for tr in table.select('tr'):
                    td_list = tr.select('td')

                    if td_list[0].text == 'Середній рейтинговий бал зарахованих на контракт':
                        spec['contract'] = td_list[1].text
                        sleep(1)

                    if td_list[0].text == 'Мінімальний рейтинговий бал серед зарахованих на бюджет':
                        spec['budget'] = td_list[1].text
                        break

                DatabaseMapper().add_speciality(spec)
                DatabaseMapper().write_coefficients(coefficients, spec)

    @staticmethod
    def get_coefficients(soup):

        znos = []
        first = soup.find('li', class_='subject_1')
        znos.append({'name': first.find('b').text, 'coefficient': first.find(
            'span', class_='coef').text, 'required': True})
        second = soup.find('li', class_='subject_2')
        znos.append({'name': second.find('b').text, 'coefficient': second.find(
            'span', class_='coef').text, 'required': True})
        tb = soup.find('li', class_='subject_3')
        third = tb.findAll('div', class_=re.compile(r'sub_\d+'))

        for subject in third:
            znos.append({'name': subject.find('b').text,
                         'coefficient': subject.find('span', class_='coef').text,
                         'required': False})

        attestat = soup.find('li', class_='subject_100')
        znos.append({'name': attestat.find('b').text, 'coefficient': attestat.find(
            'span', class_='coef').text, 'required': True})

        return znos


if __name__ == '__main__':
    Parser.get_areas()
