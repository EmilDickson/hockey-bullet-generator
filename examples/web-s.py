# Här är en enkel webscraper som lyfter ut veganska e-nummer från sidan nedan.

from lxml import html
import requests

# Inga konstigheter, hämta sidan.
page = requests.get('https://www.vegosvar.se/vilka-enummer-ar-veganska')
# Inga konstigheter heller, bygg en trädstruktur från resultatet av ovan.
tree = html.fromstring(page.content)

# Kul xpath-övning som betyder "plocka först alla divs som har ett id=xyz, 
# därefter alla element som är <b></b> och sug ut den text som finns där i"
animal_codes = tree.xpath('//div[@id="5665f2210dbecd972c701203"]//b/text()')
# Detta var ju då inte lika kul eftersom att de inte har delat in grejer i egna divs.
# Resten av skiten ligger som ren text under rubriker. Får hitta på nåt annat där.
non_animal_codes = tree.xpath('//div[@id="5665f2210dbecd972c701203"]//b/text()')

# Skriv ut, allt är en lista av strängar.
print(animal_codes)