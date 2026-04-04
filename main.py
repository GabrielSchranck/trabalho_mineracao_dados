from webcrawlers import NBAScraping
from analyze import Analyze

def main():

    print("Iniciando scraping...")
    
    download = NBAScraping(
        url='https://www.lojanba.com'
    )

    download.extract_data()

    download.upload_product()
    
    print("Iniciando análise de dados...")
    
    analyze = Analyze()
    
    analyze.load_analyze()

if __name__ == '__main__':
    main()