import re
q = "Does a police officer in Bangladesh need a warrant to arrest someone for 'Anticipatory Bail' under Section 438 of the CrPC?"
print(re.search(r'\bcrpc\b', q, re.IGNORECASE))
