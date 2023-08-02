Uses selenium to scrape sustainalytics website (sustainalytics.com/esg-scraper) for ESG ratings. For more on esg ratings, look here: [[https://www.mdpi.com/2071-1050/13/21/11663]] (ESG Paper) (publicly available)

Also, searched company does not have to match with the company names in the sustainalyitcs database. Script will itereate over parts of the company name and use sklearn TfidfVectorizer and cosine similarity to find best possible result.
