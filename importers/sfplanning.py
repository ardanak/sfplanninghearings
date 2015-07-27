# coding=utf-8
from bs4 import BeautifulSoup
from datetime import datetime
from base import DataImporter
import requests
import re

class SFPlanningNoticeImporter(DataImporter):
    """ Fetch records from www.sf-planning.org """

    importer_name = 'sfplanning'
    source = None

    def __init__(self, html, isfile):
        if isfile is True:
            self.source = self.load_file(html)
        else:
            self.source = self.load_url(html)

    @staticmethod
    def load_file(filename):
        html = open(filename, 'r').read()
        return html

    @staticmethod
    def load_url(url):
        html = requests.get(url).text
        return html

    @staticmethod
    def convert_month(string):
        string = string.strip()
        if string == 'January':
            return '01'
        elif string == 'February':
            return '02'
        elif string == 'March':
            return '03'
        elif string == 'April':
            return '04'
        elif string == 'May':
            return '05'
        elif string == 'June':
            return '06'
        elif string == 'July':
            return '07'
        elif string == 'August':
            return '08'
        elif string == 'September':
            return '09'
        elif string == 'October':
            return '10'
        elif string == 'November':
            return '11'
        elif string == 'December':
            return '12'

    def fetch(self,last_updated=datetime(1900, 1, 1)):
        """ Parses notice of hearing data (hearing type:sf_noh) from the Online Notice of Hearings page """

        soup = BeautifulSoup(self.source, "html.parser")

        content = soup.select(".content")[0]

        # getting rid of style and script tags
        map(lambda d: d.extract(), content.select('style'))
        map(lambda d: d.extract(), content.select('script'))

        # extracting <table> data
        table = content.tbody

        # getting rid of span tags
        for s in table.find_all("span"):
            s.unwrap()

        rows = table.find_all('tr', recursive=False)

        for r in rows:
            # find the date that the announcement was published online
            date_pub = r.div['id'].strip()
            date_pub_split = re.split('/', date_pub)
            date_published = date_pub_split[2] + date_pub_split[0] + date_pub_split[1]

            item = r.find('h3', text=re.compile("SAN.FRANCISCO.+PLANNING.+COMMISSION.+NOTICE.+OF.+HEARINGS", flags=re.I))

            if item is not None:
                # find hearing date
                date_p = item.find_next('p')
                date = date_p.find(text=re.compile("Thursday.+2015", re.IGNORECASE))

                if date is not None:
                    no_hearing = date_p.find(text=re.compile("no Planning Commission hearing", flags=re.I))
                    # check for "no hearing" announcements
                    if no_hearing is None:
                        p_text = date_p.get_text()
                        agenda_date = re.findall(re.compile("Thursday.+2015", re.IGNORECASE), p_text)
                        date_raw = re.split(", ", agenda_date[0])
                        month_day = re.split(" ", date_raw[1])
                        # convert month_day string to a MMDD number format
                        month = self.convert_month(month_day[0])
                        day = month_day[1]
                        if len(day) == 1:
                            day = "0" + day
                        date_formatted = date_raw[2] + month + day
                    else:
                        date_formatted = ""
            else:
                date_formatted = ""
            if date_formatted is None:
                date_formatted = ""

            """
            Get individual agendas by looping over
            paragraphs after h3 Notice of Hearings tag
            """
            headings = r.find_all('h3')
            weekly_notices = list()
            for h in headings:
                curr_h = h
                regx = re.compile(r'\s+')
                title = str(re.sub(regx, ' ', h.get_text().strip()))
                if title=="SAN FRANCISCO PLANNING COMMISSION NOTICE OF HEARINGS":
                    next = curr_h.next_sibling
                    while next is not None:
                        if str(next.name) == 'p':
                            if next.get_text() is not None:
                                p_text = next.get_text().encode('utf8')
                                if p_text == "----":
                                    next = None
                                    break
                            if next.find(text = re.compile("Thursday.+2015", re.IGNORECASE)) is None:
                                children = next.children
                                newsoup = ''
                                for child in children:
                                    newsoup = newsoup + re.sub( regx, ' ', child.encode('utf8').strip() )

                                soupify = BeautifulSoup( newsoup, "html.parser" )

                                # preserve external links
                                a_tags = soupify.find_all('a')
                                links = list()
                                if a_tags is not None:
                                    for tag in a_tags:
                                        href = str(tag.get('href'))
                                        if re.match(re.compile("^[mM]ailto.+"), href) is not None:
                                            tag.unwrap()
                                        else:
                                            if str(tag.get('target')) == '_self':
                                                href = "http://www.sf-planning.org" + str(tag['href']).strip()
                                                links.append({"href": href})
                                            else:
                                                links.append({"href": str(tag['href'])})
                                            if re.match(re.compile("^http.+", re.IGNORECASE), str(tag.get_text())) is not None:
                                                tag.unwrap()
                                            else:
                                                tag.extract()
                                # preserve image data if it exists
                                img_tags = soupify.find_all('img')
                                images = list()
                                if img_tags is not None:
                                    for tag in img_tags:
                                        images.append({"source": tag['src'], "description": tag['alt']})

                                # get announcement
                                announcement = soupify.get_text().encode('utf8').replace('\xc2\xa0', ' ').replace('Authorizationto', 'Authorization to')

                                # initialize case_num, case_code, and address fields in case no matches are found below
                                case_num = 'none_found'
                                case_code = ''
                                address = ''

                                announcement = re.sub(r'^\s*case\s*(#|no.|case#|\s+)*\s*', '', announcement, flags=re.I|re.U)
                                m = re.search(r'(\d{4}[-–.]\d+)(\S+?)(:|\s)+(.+?)\s*(,|[-–]\s+\D)', announcement, flags=re.U )
                                if m is not None:
                                    case_num = re.sub(r'[-–.]', '.', m.group(1) )
                                    case_code = m.group(2)
                                    address = re.sub(r'\W+$', '', re.sub(r'–', '-', m.group(4) ))

                                # Save individual announcements for the current week
                                weekly_notices.append({
                                    "date_published" : date_published,
                                    "date" : date_formatted,
                                    "case_num" : case_num,
                                    "case_code" : case_code,
                                    "address" : address,
                                    "links" : links,
                                    "images" : images,
                                    "announcement" : announcement
                                })
                        elif str(next.name) == "h3":
                            break
                        next = next.next_sibling
                """
                Check for fragmented notices and merge them
                Cases of fragmentation:
                    announcement is empty, this means <b>links</b> or <b>images</b> is not empty.
                    announcement starts with "For further information"
                """
                previous = None
                j = 0
                while j < len(weekly_notices):
                    notice = weekly_notices[j]

                    if previous is None:
                        previous = notice
                    elif re.match( re.compile("^\s*$"), notice['announcement'] ) is not None:
                        # merge with prior item
                        previous['links'].extend(notice['links'])
                        previous['images'].extend(notice['images'])

                        # remove duplicate item
                        del weekly_notices[j]
                        j -= 1
                    elif re.match( re.compile( "^For.+further.+information.+", re.IGNORECASE ) , notice['announcement'] ) is not None:
                        # merge with prior item
                        previous['announcement'] = previous['announcement'] + ' ' + notice['announcement']
                        previous['links'].extend( notice['links'] )
                        previous['images'].extend( notice['images'] )

                        # remove duplicate item
                        del weekly_notices[j]
                        j -= 1
                    elif re.match( re.compile( "^\s*[0-9][0-9]/[0-9][0-9]/[0-9][0-9][0-9][0-9]\s*$" ), notice['announcement'] ) is not None:
                        if notice['links'] is None and notice['images'] is None:
                            del weekly_notices[j]
                            j -= 1
                        else:
                            previous['announcement'] = previous['announcement'] + ' ' + notice['announcement']
                            previous['links'].extend( notice['links'] )
                            previous['images'].extend( notice['images'] )

                            # remove duplicate item
                            del weekly_notices[j]
                            j -= 1
                    elif notice['case_num']=='none_found' and previous['case_num']!='none_found':
                        # merge with prior item
                        previous['links'].extend(notice['links'])
                        previous['images'].extend(notice['images'])
                        previous['announcement'] = previous['announcement'] + ' ' + notice['announcement']
                        # remove duplicate item
                        del weekly_notices[j]
                        j -= 1
                    else:
                        previous = notice

                    j += 1

            # extract case number and insert notices for current week into elasticsearch database
            for notice in weekly_notices:
                caseinfo = re.search(r'(\d{4}[-–.]\d+)\s*(\D*)(\s*\S*?)', notice['announcement'], flags =re.I )
                if caseinfo is not None:
                    notice['case_num'] = re.sub(r'[-–.]', '', caseinfo.group(1) )
                    notice['case_code'] = re.split(' ', caseinfo.group(2) )[0].rstrip('.').rstrip(':').replace('.','').replace('-','')
                if len(notice['address']) > 110:
                    notice['address'] = ''
                server_y = str(datetime.today().year)
                server_m = str(datetime.today().month)
                if len(server_m) == 1:
                    server_m = '0' + server_m
                server_d = str(datetime.today().day)
                if len(server_d) == 1:
                    server_d = '0' + server_d
                server_date = server_y + server_m + server_d
                yield ('notice', {
                    'date_published': date_published,
                    'hearing_date': notice['date'],
                    'last_updated': server_date,
                    'case_num': notice['case_num'],
                    'case_code': notice['case_code'],
                    'address': notice['address'],
                    'announcement': notice['announcement'],
                    'links': notice['links'],
                    'images': notice['images']
                })
