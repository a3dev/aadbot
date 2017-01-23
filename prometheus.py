import timesofindia
import ndtv
import economictimes
import indiatoday
import redditText

class DomainNotSupportedException(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)

def getArticle(url):
	print("[0][PROMETHEUS]")
	print("url : ", url)
	articleDict = {}
	
	#timesofindia.indiatimes.com | ndtv.com | indiatoday.intoday.in | economictimes.indiatimes.com |
	TIMES_OF_INDIA = 'timesofindia.indiatimes.com'
	NDTV = 'ndtv.com'
	INDIA_TODAY = 'indiatoday.intoday.in'
	ECONOMIC_TIMES = 'economictimes.indiatimes.com'

	try:    
		if TIMES_OF_INDIA in url:
			articleDict = timesofindia.getArticle(url)
		elif NDTV in url:
			articleDict = ndtv.getArticle(url)
		elif INDIA_TODAY in url:
			articleDict = indiatoday.getArticle(url)
		elif ECONOMIC_TIMES in url:
			articleDict = economictimes.getArticle(url)
		else:
			print("[-1][PROMETHEUS][ERROR][DOMAIN NOT SUPPORTED]")
			raise DomainNotSupportedException(url)
	except Exception as e:
		print("[-1][PROMETHEUS][ERROR] : ", e)
		raise
	
	print("[1][PROMETHEUS]")
	
	credit_text = redditText.superscript('Rendered by PROMETHEUS')
	articleDict['credit'] = credit_text
	return articleDict