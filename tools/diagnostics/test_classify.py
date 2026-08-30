import sys
import re

ACT_NAME_MAP = {
    r'nat act|non.?agricultural tenancy act': 'The Non-Agricultural Tenancy Act, 1949',
    r'land reforms act|bhumi sanskar|land reform 2023': 'The Land Reforms Act, 2023',
    r'\bsat act\b|state acquisition.*tenancy|sat 1950': 'The State Acquisition and Tenancy Act, 1950',
    r'transfer of property act|\btpa\b': 'The Transfer of Property Act, 1882',
    r'trademarks? act|trademark 2009': 'The Trademarks Act, 2009',
    r'penal code|ipc|pc\b': 'The Penal Code, 1860',
    r'code of criminal procedure|crpc': 'Code of Criminal Procedure, 1898',
    r'code of civil procedure|cpc': 'Code of Civil Procedure, 1908',
    r'evidence act': 'The Evidence Act, 1872',
    r'limitation act': 'The Limitation Act, 1908',
    r'labour act|labor act': 'Bangladesh Labour Act, 2006',
    r'income tax act|income tax ordinance': 'Income Tax Act, 2023',
    r'hindu succession|hindu women.*property': "The Hindu Women's Rights to Property Act, 1937",
    r'muslim family laws?': 'Muslim Family Laws Ordinance, 1961',
    r'civil courts? act': 'The Civil Courts Act, 1887',
    r'specific relief act|\bsra\b': 'The Specific Relief Act, 1877',
    r'contract act': 'The Contract Act, 1872',
    r'registration act': 'The Registration Act, 1908',
    r'partnership act': 'The Partnership Act, 1932',
    r'sale of goods act': 'The Sale of Goods Act, 1930',
}

query = "Does a police officer in Bangladesh need a warrant to arrest someone for 'Anticipatory Bail' under Section 438 of the CrPC?"

detected_act = None
for pattern, act_name in ACT_NAME_MAP.items():
    if re.search(pattern, query, re.IGNORECASE):
        detected_act = act_name
        break

print('Detected Act:', detected_act)
