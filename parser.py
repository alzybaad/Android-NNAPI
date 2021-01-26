import requests
from bs4 import BeautifulSoup

target_api_levels = (27, 28, 29, 30)
android_os_versions = (8.1, 9, 10, 11)

def getHeader(tr_element):
    th_elements = tr_element.find_all('th')
    return (th_elements[0].text, th_elements[1].text)

def getOperations(tr_elements):
    operations = []

    for tr_element in tr_elements:
        td_elements = tr_element.find_all('td')

        category = td_elements[0].text
        for li_element in td_elements[1].find_all('li'):
            a_element = li_element.find('a')
            operations.append((category, a_element.text, a_element['href']))

    return operations

def loadOperations():
    html = requests.get('https://developer.android.com/ndk/guides/neuralnetworks')
    soup = BeautifulSoup(html.content, 'html.parser')

    tr_elements = soup.find('table').find_all('tr')
    return (getHeader(tr_elements[0]), getOperations(tr_elements[1:]))

def getInfoElement(element):
    while element.name != 'td':
        element = element.parent

    info_element = element.next_element
    while info_element.name != 'td':
        info_element = info_element.next_element

    return info_element

def getSupportingApiLevels(info_element):
    return [target_api_level for target_api_level in target_api_levels if 'since API level {}'.format(target_api_level) in info_element.text]

def loadSupportingApiLevels(operations):
    html = requests.get('https://developer.android.com/ndk/reference/group/neural-networks')
    soup = BeautifulSoup(html.content, 'html.parser')

    supporting_api_levels = []

    for operation in operations:
        operation_id = operation[2][operation[2].index('#'):]
        element = soup.select_one(operation_id)
        info_element = getInfoElement(element)
        supporting_api_levels.append(getSupportingApiLevels(info_element))

    return supporting_api_levels

def createHeader(header):
    line1 = '|{}|{}|'.format(header[0], header[1])
    line2 = '|:--|:--|'

    for target_api_level, android_os_version in zip(target_api_levels, android_os_versions):
        line1 += 'API level {}<br/>(Android {})|'.format(target_api_level, android_os_version)
        line2 += ':--|'

    return '{}\n{}\n'.format(line1, line2)

def createCategory(operation, last_category):
    return operation[0] if last_category != operation[0] else ''

def createOperation(operation):
    return '[{}](https://developer.android.com{})'.format(operation[1], operation[2])

def createSupportingApiLevels(supporting_api_level):
    return '|'.join(['✓' if target_api_level in supporting_api_level else '' for target_api_level in target_api_levels])

def createMarkdown(header, operations, supporting_api_levels):
    markdown = createHeader(header)

    last_category = ''

    for operation, supporting_api_level in zip(operations, supporting_api_levels):
        markdown += '|{}|{}|{}|\n'.format(createCategory(operation, last_category), createOperation(operation), createSupportingApiLevels(supporting_api_level)) 

        last_category = operation[0]

    return markdown

def writeMarkdown(filename, markdown):
    with open(filename, mode='w') as file:
        file.write('# Android NNAPI Supporting Operations\n\n')
        file.write(markdown)

if __name__ == '__main__':
    (header, operations) = loadOperations()
    supporting_api_levels = loadSupportingApiLevels(operations)
    markdown = createMarkdown(header, operations, supporting_api_levels)
    writeMarkdown('README.md', markdown)
