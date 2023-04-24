import scrapy
import asyncio
from pyppeteer import launch


class ShampooDataSpider(scrapy.Spider):
    name = "shampoo_data"
    start_urls = ["https://www.flipkart.com/l-oreal-paris-dream-lengths-shampoo-1-ltr/p/itm2584abbb20afc?pid=SMPFZH5HMGWCQZPF&lid=LSTSMPFZH5HMGWCQZPFIKYPOD&marketplace=FLIPKART&q=shampoo&store=g9b%2Flcf%2Fqqm%2Ft36&srno=s_1_2&otracker=search&otracker1=search&fm=Search&iid=fd6b5221-34aa-4d84-8d5c-45d7942ee75f.SMPFZH5HMGWCQZPF.SEARCH&ppt=sp&ppn=sp&ssid=wvowqwu40w0000001679047209465&qH=186764a607df448c"]

    async def parse(self, response):
        # Launch a new browser instance
        browser = await launch(headless=True)
        page = await browser.newPage()

        # Navigate to the product page
        await page.goto(response.url)
       
        # Get the div tag with class="_1MR4o5"

        breadcrumb_divs = await page.querySelectorAll('div._1MR4o5 div')

        if len(breadcrumb_divs) >= 2:
            
            div_target = await page.querySelector('div._1MR4o5 div:nth-last-child(2)')

            brand_name = await div_target.querySelectorEval('a._2whKao', "el => el.textContent")
        else:
            brand_name = None

        # Get the div tag with class="aMaAEs"
        div_aMaAEs = await page.querySelector('div.aMaAEs')

        if div_aMaAEs:
            # Get the product name
            product_name = await div_aMaAEs.querySelectorEval('span.B_NuCI', 'el => el.textContent')

            # Get the price
            price = await div_aMaAEs.querySelectorEval('div._30jeq3._16Jk6d', 'el => el.textContent')
        else:
            product_name = None
            price = None

        # Get the description
        description = await page.querySelectorEval('div._1mXcCf, div._1mXcCf.RmoJUa', 'el => el.textContent')

        # Interact with the input field and the span tag and extract the innerHTML of the target div element
        await page.type('input._36yFo0', '4000125')
        await asyncio.sleep(1)
        await page.click('span._2P_LDn')
        await page.waitForSelector('div._3XINqE', timeout=10000)
        delivery_code = await page.querySelectorEval('div._3XINqE', 'el => el.innerHTML')

        quantity_options = []
        els = await page.querySelectorAll('a._1fGeJ5, a._1fGeJ5.PP89tw')
        for el in els:
            quantity_options.append({
                'quantity': await (await el.getProperty('textContent')).jsonValue(),
                'href': await (await el.getProperty('href')).jsonValue()
            })

        for item in quantity_options:
            await page.goto(item["href"], waitUntil='networkidle2', timeout=10000)
            product_div = await page.querySelector('div.aMaAEs')
            item['price'] = await product_div.querySelectorEval('div._30jeq3._16Jk6d', 'el => el.textContent')

        
        

        # Close the browser instance
        await page.close()

        # Create a dictionary of the scraped data
        data = {
            'brand_name': brand_name,
            'product_name': product_name.strip(),
            'price': price.strip(),
            'delivery_code': delivery_code,
            'quantity_options': quantity_options,
            'description': description.strip(),
        }

        yield data
